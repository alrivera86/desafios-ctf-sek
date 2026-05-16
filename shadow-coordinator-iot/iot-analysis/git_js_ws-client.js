/**
 * WebSocket client — mimics Home Assistant's websocket_api.
 * Handshake: server sends `auth_required` → client replies `auth` with
 * bearer token → server responds `auth_ok` → push stream starts.
 */
(function () {
    const HA = window.HA = window.HA || {};

    class HaWebSocket extends EventTarget {
        constructor() {
            super();
            this.ws = null;
            this.nextId = 1;
            this.reconnectTimer = null;
            this.pingTimer = null;
            this.connected = false;
        }

        connect(token) {
            this.token = token;
            const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const url = `${proto}//${location.host}/api/websocket`;
            try { this.ws = new WebSocket(url); }
            catch (e) { this._scheduleReconnect(); return; }

            this.ws.addEventListener('message', (ev) => {
                let msg;
                try { msg = JSON.parse(ev.data); } catch (e) { return; }
                this._handle(msg);
            });
            this.ws.addEventListener('close', () => {
                this.connected = false;
                this.dispatchEvent(new CustomEvent('disconnected'));
                this._scheduleReconnect();
            });
            this.ws.addEventListener('error', () => { /* handled by close */ });
        }

        _scheduleReconnect() {
            if (this.reconnectTimer) return;
            this.reconnectTimer = setTimeout(() => {
                this.reconnectTimer = null;
                const token = localStorage.getItem('ha_token');
                if (token) this.connect(token);
            }, 3000);
        }

        _handle(msg) {
            if (msg.type === 'auth_required') {
                this.ws.send(JSON.stringify({ type: 'auth', access_token: this.token }));
                return;
            }
            if (msg.type === 'auth_ok') {
                this.connected = true;
                this.dispatchEvent(new CustomEvent('connected'));
                this.send({ type: 'subscribe_events', event_type: 'state_changed' });
                this._startPing();
                return;
            }
            if (msg.type === 'auth_invalid') {
                this.dispatchEvent(new CustomEvent('auth_invalid'));
                return;
            }
            this.dispatchEvent(new CustomEvent('message', { detail: msg }));
        }

        send(msg) {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
            if (!msg.id) msg.id = this.nextId++;
            this.ws.send(JSON.stringify(msg));
            return msg.id;
        }

        _startPing() {
            if (this.pingTimer) clearInterval(this.pingTimer);
            this.pingTimer = setInterval(() => this.send({ type: 'ping' }), 20000);
        }

        close() {
            if (this.ws) { try { this.ws.close(); } catch (e) {} }
        }
    }

    HA.ws = new HaWebSocket();
})();
