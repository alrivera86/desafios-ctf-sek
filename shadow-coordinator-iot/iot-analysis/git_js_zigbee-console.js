/**
 * Zigbee live packet console — streams packets pushed via WS.
 */
(function () {
    const HA = window.HA = window.HA || {};

    let paused = false;
    const MAX_ROWS = 300;

    function append(packet) {
        if (paused) return;
        const host = document.getElementById('zigbeeConsole');
        if (!host) return;
        const ts = new Date(packet.ts).toLocaleTimeString('en-GB', { hour12: false }) + '.' + String(new Date(packet.ts).getMilliseconds()).padStart(3, '0');
        const type = typeLabelClass(packet);
        const row = document.createElement('div');
        row.className = `pkt ${type}`;
        row.innerHTML = `
            <time>${ts}</time>
            <span class="src">${packet.src || '------'}</span>
            <span class="dst">${packet.dst || '------'}</span>
            <span class="desc">${describe(packet)}</span>
        `;
        host.appendChild(row);
        while (host.children.length > MAX_ROWS) host.removeChild(host.firstChild);
        host.scrollTop = host.scrollHeight;
    }

    function typeLabelClass(packet) {
        if (packet.subtype === 'LINK_STATUS') return 'type-linkstatus';
        if (packet.subtype === 'ROUTE_REQUEST') return 'type-route';
        if (packet.subtype === 'DEVICE_ANNOUNCE') return 'type-announce';
        if (packet.subtype === 'REPORT_ATTRIBUTES') return 'type-report';
        if (packet.subtype === 'ACK') return 'type-ack';
        return '';
    }

    function describe(packet) {
        if (packet.subtype === 'DEVICE_ANNOUNCE') {
            return `Device Announce · nwk=${packet.announce.nwk_address} ieee=${packet.announce.ieee_address}`;
        }
        if (packet.subtype === 'LINK_STATUS') {
            return `Link Status · ${packet.entries.length} neighbours`;
        }
        if (packet.subtype === 'ROUTE_REQUEST') {
            return `Route Request → ${packet.target}`;
        }
        if (packet.subtype === 'REPORT_ATTRIBUTES') {
            return `ZCL Report · ${packet.cluster_name} attr=${packet.attribute} value=${packet.value}`;
        }
        if (packet.subtype === 'ACK') {
            return `MAC Ack`;
        }
        return `${packet.frame_type} ${packet.subtype}`;
    }

    function clear() {
        const host = document.getElementById('zigbeeConsole');
        if (host) host.innerHTML = '';
    }

    function togglePause(btn) {
        paused = !paused;
        if (btn) btn.innerText = paused ? 'Resume' : 'Pause';
    }

    HA.zigbeeConsole = { append, clear, togglePause, get paused() { return paused; } };
})();
