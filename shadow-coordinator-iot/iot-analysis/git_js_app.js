/**
 * Main application shell: login, navigation, WebSocket wiring, tile click
 * handlers, developer tools form.
 */
(function () {
    const HA = window.HA = window.HA || {};
    const $ = (id) => document.getElementById(id);
    const q = (sel) => document.querySelectorAll(sel);

    HA.toast = function toast(message, kind = '') {
        const host = $('toastHost');
        const el = document.createElement('div');
        el.className = 'toast ' + kind;
        el.textContent = message;
        host.appendChild(el);
        setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 250); }, 3200);
    };

    let currentView = 'overview';

    function showApp() { $('loginScreen').classList.add('hidden'); $('appShell').classList.remove('hidden'); }
    function hideApp() { $('loginScreen').classList.remove('hidden'); $('appShell').classList.add('hidden'); }

    function switchView(view) {
        currentView = view;
        q('.nav-item').forEach((b) => b.classList.toggle('active', b.dataset.view === view));
        q('.ha-view').forEach((v) => v.classList.toggle('active', v.id === `view-${view}`));
        const button = document.querySelector(`.nav-item[data-view="${view}"]`);
        if (button) {
            const span = button.querySelector('span');
            $('viewTitle').textContent = span ? span.textContent : 'Home Assistant';
        }
        const tabsVisible = view === 'overview';
        $('appbarTabs').style.visibility = tabsVisible ? 'visible' : 'hidden';
        hydrate(view);
    }

    async function hydrate(view) {
        try {
            if (view === 'overview') {
                await Promise.all([HA.views.loadEntities(), HA.views.loadLogbook()]);
            } else if (view === 'logbook') {
                await HA.views.loadLogbook();
            } else if (view === 'history') {
                await HA.views.loadHistory();
            } else if (view === 'energy') {
                await HA.views.loadEnergy();
            } else if (view === 'map') {
                await HA.views.loadMap();
            } else if (view === 'zigbee') {
                await HA.views.loadZigbee();
            } else if (view === 'developer') {
                await HA.views.loadDeveloper();
                refreshDevServicesSuggestions();
            } else if (view === 'notifications') {
                await HA.views.loadNotifications();
            } else if (view === 'settings') {
                await HA.settings.render();
            }
        } catch (e) {
            console.error('hydrate error', e);
            if (e.status === 401) tokenInvalidated();
        }
    }

    function tokenInvalidated() {
        localStorage.removeItem('ha_token');
        hideApp();
    }

    async function login(username, password) {
        const resp = await fetch('/api/v2/auth/login', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        if (!resp.ok) {
            const data = await resp.json().catch(() => ({ message: 'Invalid credentials' }));
            throw new Error(data.message || 'Invalid credentials');
        }
        const data = await resp.json();
        localStorage.setItem('ha_token', data.access_token);
        localStorage.setItem('ha_user', JSON.stringify(data.user || {}));
        return data;
    }

    function applyRoleUI(user) {
        $('profileName').textContent = user?.name || 'User';
        $('avatarLetter').textContent = (user?.name || 'U')[0].toUpperCase();
        const pill = $('roleBadge');
        if (pill) {
            pill.textContent = user?.role || 'user';
            pill.className = 'role-pill role-' + (user?.role || 'user');
        }
        document.body.classList.toggle('role-owner', user?.role === 'owner');
        document.body.classList.toggle('role-user', user?.role === 'user');
    }

    function setupWS() {
        const token = localStorage.getItem('ha_token');
        if (!token) return;
        HA.ws.connect(token);

        const indicator = $('connIndicator');
        const connText = indicator?.querySelector('.conn-text');

        HA.ws.addEventListener('connected', () => {
            indicator?.classList.remove('err');
            indicator?.classList.add('ok');
            if (connText) connText.textContent = 'Live';
        });
        HA.ws.addEventListener('disconnected', () => {
            indicator?.classList.remove('ok');
            indicator?.classList.add('err');
            if (connText) connText.textContent = 'Reconnecting';
        });
        HA.ws.addEventListener('auth_invalid', () => tokenInvalidated());

        HA.ws.addEventListener('message', (ev) => {
            const msg = ev.detail;
            if (msg.type === 'sim_tick') {
                (msg.packets || []).forEach((p) => HA.zigbeeConsole.append(p));
                (msg.state_changes || []).forEach((c) => {
                    const entity = HA.views.entityCache[c.entity_id];
                    if (entity && !entity.user_override) {
                        entity.state = c.state;
                        if (c.unit) entity.unit = c.unit;
                    }
                });
                if ((msg.state_changes || []).length) {
                    HA.views.renderOverviewMetrics();
                    HA.views.renderEntityList();
                    HA.views.refreshActiveDashboard();
                }
                (msg.logbook || []).forEach((entry) => prependLogbook(entry));
                const rate = $('zigbeePacketRate');
                if (rate) rate.textContent = `${msg.packet_rate || 0} pps`;
                // also update network dashboard pps counter if visible
                const netRate = $('netPacketRateLabel');
                if (netRate && document.querySelector('.dashboard-panel[data-dashboard="network"].active')) {
                    netRate.textContent = `${msg.packet_rate || 0} pps`;
                }

                (msg.packets || []).forEach((p) => {
                    if (p.src && p.dst && p.dst !== '0xFFFF' && p.dst !== '0xFFFD') HA.meshMap.flashLink(p.src, p.dst);
                });
            } else if (msg.type === 'state_override') {
                const entity = HA.views.entityCache[msg.entity_id];
                if (entity) { entity.state = msg.state; entity.user_override = true; entity.overridden_by = msg.by; }
                HA.views.renderOverviewMetrics();
                HA.views.renderEntityList();
                HA.views.refreshActiveDashboard();
                prependLogbook({ time: new Date().toTimeString().slice(0, 5), source: msg.entity_id, message: `Set to ${msg.state} by ${msg.by}` });
            } else if (msg.type === 'notification_created') {
                HA.toast(`New notification: ${msg.notification.title}`, 'ok');
                if (currentView === 'notifications') HA.views.loadNotifications();
                $('notifBadge')?.classList.add('on');
                $('notifDot')?.classList.add('on');
            } else if (msg.type === 'logbook_append') {
                prependLogbook(msg.entry);
            } else if (msg.type === 'automation_changed') {
                if (currentView === 'settings' && HA.settings.currentView === 'automations') HA.settings.render();
            }
        });
    }

    function prependLogbook(entry) {
        const ts = $('activityTs'); if (ts) ts.textContent = new Date().toLocaleTimeString();
        ['activityList', 'logbookList'].forEach((id) => {
            const host = $(id); if (!host) return;
            const el = document.createElement('div');
            el.className = 'activity';
            el.innerHTML = `<time>${entry.time}</time><div><strong>${entry.source}</strong><span>${entry.message}</span></div>`;
            host.insertBefore(el, host.firstChild);
            while (host.children.length > 40) host.removeChild(host.lastChild);
        });
    }

    // Tile / entity click → more-info.  A tile is either
    //   - a DOM element with data-entity-click (rendered by JS lists), or
    //   - a .entity-tile that contains a child element with data-entity.
    function wireEntityClicks() {
        document.body.addEventListener('click', (ev) => {
            let id = null;
            const explicit = ev.target.closest('[data-entity-click]');
            if (explicit) id = explicit.dataset.entityClick;
            if (!id) {
                const tile = ev.target.closest('.entity-tile');
                if (tile) {
                    const holder = tile.querySelector('[data-entity]');
                    if (holder) id = holder.dataset.entity;
                }
            }
            if (!id) {
                const direct = ev.target.closest('[data-entity]');
                if (direct) id = direct.dataset.entity;
            }
            if (!id || id === 'sensor.main_door_nwk_address') return;
            HA.views.openMoreInfo(id);
        });
    }

    function refreshDevServicesSuggestions() {
        const datalist = $('devServiceList');
        if (!datalist) return;
        const suggestions = [
            'lock.lock', 'lock.unlock',
            'switch.turn_on', 'switch.turn_off', 'switch.toggle',
            'light.turn_on', 'light.turn_off', 'light.toggle',
            'script.script_mesh_healthcheck',
            'scene.scene_evening_security',
            'persistent_notification.create',
            'persistent_notification.dismiss',
            'homeassistant.restart', 'homeassistant.check_config',
        ];
        datalist.innerHTML = suggestions.map((s) => `<option value="${s}">`).join('');
    }

    document.addEventListener('DOMContentLoaded', () => {
        const storedToken = localStorage.getItem('ha_token');
        if (storedToken) {
            fetch('/api/v2/auth/me', { headers: { 'Authorization': 'Bearer ' + storedToken } })
                .then((r) => r.ok ? r.json() : Promise.reject())
                .then((me) => {
                    localStorage.setItem('ha_user', JSON.stringify(me));
                    applyRoleUI(me);
                    showApp();
                    setupWS();
                    hydrate('overview');
                })
                .catch(() => tokenInvalidated());
        }

        $('loginForm').addEventListener('submit', async (ev) => {
            ev.preventDefault();
            $('loginError').textContent = '';
            try {
                const data = await login($('username').value.trim(), $('password').value);
                applyRoleUI(data.user);
                showApp();
                setupWS();
                hydrate('overview');
            } catch (e) {
                $('loginError').textContent = e.message;
            }
        });

        $('profileBtn')?.addEventListener('click', () => {
            if (confirm('Log out?')) {
                localStorage.removeItem('ha_token');
                localStorage.removeItem('ha_user');
                HA.ws.close();
                hideApp();
            }
        });

        q('.nav-item').forEach((btn) => btn.addEventListener('click', () => switchView(btn.dataset.view)));
        q('.settings-menu button').forEach((btn) => btn.addEventListener('click', () => HA.settings.render(btn.dataset.settings)));

        $('toggleSidebar')?.addEventListener('click', () => $('sidebar').classList.toggle('open'));
        $('notifBtn')?.addEventListener('click', () => switchView('notifications'));
        $('searchBtn')?.addEventListener('click', () => {
            const q = prompt('Search entities:');
            if (!q) return;
            const match = Object.values(HA.views.entityCache).find((e) =>
                e.entity_id.includes(q.toLowerCase()) || (e.name || '').toLowerCase().includes(q.toLowerCase())
            );
            if (match) HA.views.openMoreInfo(match.entity_id);
            else HA.toast('No entities matched', 'warn');
        });
        $('moreBtn')?.addEventListener('click', () => {
            const options = [
                'c: Check configuration',
                'r: Restart Home Assistant',
                'b: Create backup',
                'cancel',
            ].join('\n');
            const pick = prompt(`Choose an action:\n${options}`);
            if (pick === 'c') HA.views.api('/api/v2/services/homeassistant/check_config', { method: 'POST', body: '{}' }).then(() => HA.toast('Configuration valid', 'ok'));
            if (pick === 'r') HA.views.api('/api/v2/services/homeassistant/restart', { method: 'POST', body: '{}' }).then(() => HA.toast('Restart scheduled', 'ok'));
            if (pick === 'b') HA.views.api('/api/v2/config/backups', { method: 'POST', body: JSON.stringify({ note: 'Quick action backup' }) }).then((r) => HA.toast(`Backup ${r.backup.id}`, 'ok'));
        });

        $('zigbeePause')?.addEventListener('click', (ev) => HA.zigbeeConsole.togglePause(ev.target));
        $('zigbeeClear')?.addEventListener('click', () => HA.zigbeeConsole.clear());
        $('regenCapture')?.addEventListener('click', async () => {
            const btn = $('regenCapture'); btn.disabled = true; btn.textContent = 'Regenerating…';
            try {
                const j = await HA.views.api('/api/v2/zigbee/capture/regenerate', { method: 'POST', body: '{}' });
                HA.toast(j.status === 'ok' ? 'capture.pcap regenerated' : 'Regeneration failed', j.status === 'ok' ? 'ok' : 'err');
            } catch (e) { HA.toast(e.message, 'err'); }
            btn.disabled = false; btn.textContent = 'Regenerate';
        });

        $('devServiceForm')?.addEventListener('submit', async (ev) => {
            ev.preventDefault();
            const form = ev.target;
            const service = form.service.value.trim();
            const [domain, svc] = service.split('.');
            if (!domain || !svc) { $('devServiceResult').textContent = 'Use the format domain.service (e.g. lock.unlock)'; return; }
            const rawYaml = form.data.value;
            const parsed = parseYamlLite(rawYaml);
            try {
                const r = await HA.views.api(`/api/v2/services/${domain}/${svc}`, { method: 'POST', body: JSON.stringify(parsed) });
                $('devServiceResult').textContent = JSON.stringify(r, null, 2);
                HA.toast(`${service} dispatched`, 'ok');
                if (currentView === 'overview') HA.views.loadEntities();
            } catch (e) {
                $('devServiceResult').textContent = JSON.stringify({ status: 'error', message: e.message, detail: e.data || null }, null, 2);
                HA.toast(e.message, 'err');
            }
        });

        q('#appbarTabs .tab').forEach((tab) => tab.addEventListener('click', () => {
            q('#appbarTabs .tab').forEach((t) => t.classList.remove('active'));
            tab.classList.add('active');
            const name = tab.dataset.tab;
            // Show/hide the matching dashboard panel
            document.querySelectorAll('#view-overview .dashboard-panel').forEach((p) => {
                p.classList.toggle('active', p.dataset.dashboard === name);
            });
            if (name === 'home') {
                HA.views.loadEntities();
                HA.views.loadLogbook();
            } else if (name === 'security') {
                HA.views.loadEntities().then(() => HA.views.loadSecurityDashboard());
            } else if (name === 'network') {
                HA.views.loadNetworkDashboard();
            }
        }));

        // Alarm panel buttons
        document.addEventListener('click', (ev) => {
            const btn = ev.target.closest('[data-alarm]');
            if (!btn) return;
            HA.views.setAlarmMode(btn.dataset.alarm);
            HA.toast(`Alarm ${btn.dataset.alarm.replace('_', ' ')}`, 'ok');
            // Also create a persistent notification & service call
            HA.views.api('/api/v2/services/alarm_control_panel/' + btn.dataset.alarm, {
                method: 'POST', body: JSON.stringify({ entity_id: 'alarm_control_panel.campus' }),
            }).catch(() => {});
        });

        // Net device cards → open more-info via NWK → IEEE resolution
        document.addEventListener('click', (ev) => {
            const card = ev.target.closest('.net-device-card');
            if (!card) return;
            const nwk = card.dataset.nwk;
            if (!nwk) return;
            // Guess entity id from area for now: just open the lock for 0x7B9C
            const map = {
                '0x0000': 'sensor.zb_gw_03_status',
                '0x1A2B': 'sensor.north_hall_temperature',
                '0x3C4D': 'binary_sensor.library_occupancy',
                '0x55AA': 'device_tracker.atrium_relay',
                '0x7B9C': 'lock.main_door_smart_lock',
            };
            const eid = map[nwk];
            if (eid) HA.views.openMoreInfo(eid);
        });

        wireEntityClicks();
    });

    // Tiny YAML subset parser for the Developer Tools form. Supports k: v lines,
    // integers, booleans, strings. Good enough for the simulation.
    function parseYamlLite(text) {
        const out = {};
        text.split('\n').forEach((line) => {
            const m = line.match(/^\s*([\w.]+)\s*:\s*(.*)$/);
            if (!m) return;
            let v = m[2].trim();
            if (v.startsWith('"') && v.endsWith('"')) v = v.slice(1, -1);
            else if (v === 'true') v = true;
            else if (v === 'false') v = false;
            else if (/^-?\d+$/.test(v)) v = Number(v);
            else if (/^-?\d*\.\d+$/.test(v)) v = Number(v);
            out[m[1]] = v;
        });
        return out;
    }
})();
