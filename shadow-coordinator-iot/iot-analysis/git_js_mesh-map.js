/**
 * Mesh topology renderer — SVG nodes + animated links.  By default it
 * targets #meshMap + #mapNodeDetail but can be retargeted for embedded
 * mini-maps (e.g. the Network dashboard tab).
 */
(function () {
    const HA = window.HA = window.HA || {};

    let currentTopology = null;
    const selectedByHost = {};

    function render(topology, svgId = 'meshMap', detailId = 'mapNodeDetail') {
        currentTopology = topology;
        const svg = document.getElementById(svgId);
        if (!svg) return;
        svg.innerHTML = '';
        svg.dataset.detailId = detailId;

        const ns = 'http://www.w3.org/2000/svg';
        const nodeById = Object.fromEntries(topology.nodes.map((n) => [n.nwk, n]));

        for (const link of topology.links) {
            const from = nodeById[link.from];
            const to = nodeById[link.to];
            if (!from || !to) continue;
            const line = document.createElementNS(ns, 'line');
            line.setAttribute('class', 'mesh-link');
            line.setAttribute('x1', from.position.x);
            line.setAttribute('y1', from.position.y);
            line.setAttribute('x2', to.position.x);
            line.setAttribute('y2', to.position.y);
            line.setAttribute('data-from', link.from);
            line.setAttribute('data-to', link.to);
            svg.appendChild(line);
        }

        for (const node of topology.nodes) {
            const g = document.createElementNS(ns, 'g');
            let cls = 'mesh-node ' + (node.role === 'coordinator' ? 'coordinator' : node.role === 'router' ? 'router' : 'end');
            if (node.nwk === '0x7B9C') cls += ' warn';
            g.setAttribute('class', cls);
            g.setAttribute('transform', `translate(${node.position.x},${node.position.y})`);
            g.setAttribute('data-nwk', node.nwk);

            const circle = document.createElementNS(ns, 'circle');
            circle.setAttribute('r', node.role === 'coordinator' ? 26 : 18);
            g.appendChild(circle);

            const label = document.createElementNS(ns, 'text');
            label.setAttribute('y', node.role === 'coordinator' ? 4 : 4);
            label.textContent = node.nwk;
            g.appendChild(label);

            const sub = document.createElementNS(ns, 'text');
            sub.setAttribute('class', 'node-sub');
            sub.setAttribute('y', node.role === 'coordinator' ? 40 : 32);
            sub.textContent = node.area;
            g.appendChild(sub);

            g.addEventListener('click', () => selectNode(node.nwk, detailId));
            svg.appendChild(g);
        }

        if (selectedByHost[detailId]) selectNode(selectedByHost[detailId], detailId);
    }

    function selectNode(nwk, detailId = 'mapNodeDetail') {
        selectedByHost[detailId] = nwk;
        if (!currentTopology) return;
        const node = currentTopology.nodes.find((n) => n.nwk === nwk);
        const host = document.getElementById(detailId);
        if (!node || !host) return;
        host.innerHTML = `
            <h3>${node.name}</h3>
            <p class="muted">${node.role} · ${node.type}</p>
            <dl>
                <dt>NWK</dt><dd>${node.nwk}</dd>
                <dt>IEEE</dt><dd>${node.ieee}</dd>
                <dt>Model</dt><dd>${node.model}</dd>
                <dt>Area</dt><dd>${node.area}</dd>
                <dt>LQI</dt><dd>${node.lqi}</dd>
                <dt>Battery</dt><dd>${typeof node.battery === 'number' ? node.battery + '%' : node.battery}</dd>
                <dt>Firmware</dt><dd>${node.firmware_version || '-'}</dd>
                <dt>State</dt><dd>${node.state}</dd>
                <dt>Last seen</dt><dd>${new Date(node.last_seen).toLocaleTimeString()}</dd>
            </dl>
        `;
    }

    function flashLink(src, dst) {
        document.querySelectorAll(`.mesh-map line[data-from="${src}"][data-to="${dst}"], .mesh-map line[data-from="${dst}"][data-to="${src}"]`)
            .forEach((line) => {
                line.classList.add('active');
                setTimeout(() => line.classList.remove('active'), 1200);
            });
    }

    HA.meshMap = { render, selectNode, flashLink };
})();
