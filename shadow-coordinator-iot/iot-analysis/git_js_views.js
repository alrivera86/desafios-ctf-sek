/**
 * Renderers for non-settings views (Overview, Energy, Map, Logbook,
 * History, Zigbee, Developer tools, Notifications) and the more-info dialog.
 */
(function () {
    const HA = window.HA = window.HA || {};
    const $ = (id) => document.getElementById(id);
    const entityCache = {};

    function authedFetch(url, options = {}) {
        const token = localStorage.getItem('ha_token');
        const headers = { ...(options.headers || {}), 'Authorization': 'Bearer ' + token };
        if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
        return fetch(url, { ...options, headers });
    }

    async function api(url, options) {
        const resp = await authedFetch(url, options);
        let data = {};
        try { data = await resp.json(); } catch (e) { /* empty */ }
        if (!resp.ok) {
            const err = new Error(data.message || data.error || `HTTP ${resp.status}`);
            err.status = resp.status;
            err.data = data;
            throw err;
        }
        return data;
    }

    async function loadEntities() {
        const data = await api('/api/v2/states');
        (data.entities || []).forEach((e) => entityCache[e.entity_id] = e);
        renderOverviewMetrics();
        renderEntityList();
        return data.entities;
    }

    function stateLabel(entity) {
        if (!entity) return '—';
        if (entity.state === undefined || entity.state === null) return 'unknown';
        return `${entity.state}${entity.unit ? ' ' + entity.unit : ''}`;
    }

    function renderOverviewMetrics() {
        document.querySelectorAll('[data-entity]').forEach((el) => {
            const id = el.dataset.entity;
            if (id === 'sensor.main_door_nwk_address') return;
            const entity = entityCache[id];
            el.textContent = stateLabel(entity);
            // Add visual cue for overridden entities
            const parentTile = el.closest('.entity-tile');
            if (parentTile && entity?.user_override) parentTile.classList.add('overridden');
            else if (parentTile) parentTile.classList.remove('overridden');
        });
    }

    function renderEntityList() {
        const host = $('entityList');
        if (!host) return;
        const zigbee = Object.values(entityCache).filter((e) => e.integration === 'zha');
        const status = $('zigbeeNetworkStatus');
        if (status) status.textContent = `${zigbee.length} entities`;
        host.innerHTML = zigbee.slice(0, 10).map((e) => `
            <div class="entity-row" data-entity-click="${e.entity_id}">
                <span class="tile-icon ${entityIcon(e.entity_id)}" style="width:32px;height:32px;"><svg class="mdi" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/></svg></span>
                <div>
                    <strong>${e.name}</strong>
                    <small>${e.entity_id} · ${stateLabel(e)} · ${e.nwk || e.area || ''}</small>
                </div>
            </div>
        `).join('');
    }

    function entityIcon(entityId) {
        if (entityId.includes('temperature')) return 'temperature';
        if (entityId.includes('motion') || entityId.includes('occupancy')) return 'motion';
        if (entityId.includes('lock')) return 'lock';
        if (entityId.includes('battery')) return 'battery';
        if (entityId.includes('lqi') || entityId.includes('linkquality')) return 'signal';
        if (entityId.includes('atrium') || entityId.includes('router') || entityId.includes('tracker')) return 'router';
        return 'zigbee';
    }

    async function loadLogbook() {
        const data = await api('/api/v2/logbook');
        const html = (data.entries || []).slice(0, 30).map((entry) => `
            <div class="activity">
                <time>${entry.time}</time>
                <div><strong>${entry.source}</strong><span>${entry.message}</span></div>
            </div>
        `).join('');
        ['activityList', 'logbookList'].forEach((id) => { const el = $(id); if (el) el.innerHTML = html; });
        const ts = $('activityTs'); if (ts) ts.textContent = new Date().toLocaleTimeString();
    }

    async function loadHistory() {
        const [t, l] = await Promise.all([
            api('/api/v2/history?entity_id=sensor.north_hall_temperature'),
            api('/api/v2/history?entity_id=sensor.lqi_average'),
        ]);
        HA.charts.renderLineChart($('historyTempChart'), t.points || [], { color: '#ff9800' });
        HA.charts.renderLineChart($('historyLqiChart'), l.points || [], { color: '#03a9f4' });
    }

    async function loadEnergy() {
        const data = await api('/api/v2/energy');
        HA.charts.renderBarChart($('energyChart'), data.grid || [], { color: '#43a047' });
        $('energySummary').innerHTML = `
            <div><small>Imported</small><strong>${data.today.imported} kWh</strong></div>
            <div><small>Cost today</small><strong>$${data.today.cost}</strong></div>
            <div><small>Exported</small><strong>${data.today.exported} kWh</strong></div>
            <div><small>Produced</small><strong>${data.today.produced} kWh</strong></div>
        `;
        $('energyDevices').innerHTML = (data.devices || []).map((d) => `
            <div><span>${d.name}</span><strong>${d.kwh.toFixed(2)} kWh</strong></div>
        `).join('');
    }

    // =================================================================
    //   Overview dashboards: Home / Security / Network
    // =================================================================
    let _alarmMode = 'disarmed';

    async function loadSecurityDashboard() {
        // Posture metrics
        const entities = Object.values(entityCache);
        const lock = entities.find((e) => e.entity_id === 'lock.main_door_smart_lock');
        const occupancy = entities.find((e) => e.entity_id === 'binary_sensor.library_occupancy');
        const motion = entities.find((e) => e.entity_id === 'binary_sensor.north_hall_motion');

        const posture = $('secPosture');
        if (posture) {
            posture.innerHTML = `
                <div class="metric ${lock?.state === 'unlocked' ? 'warn' : 'ok'}">
                    <small>Main door</small>
                    <strong>${(lock?.state || 'unknown').toUpperCase()}</strong>
                </div>
                <div class="metric ${occupancy?.state === 'on' ? 'warn' : 'ok'}">
                    <small>Library</small>
                    <strong>${occupancy?.state === 'on' ? 'OCCUPIED' : 'CLEAR'}</strong>
                </div>
                <div class="metric ${motion?.state === 'on' ? 'warn' : 'ok'}">
                    <small>North Hall</small>
                    <strong>${motion?.state === 'on' ? 'MOTION' : 'CLEAR'}</strong>
                </div>
                <div class="metric ${_alarmMode !== 'disarmed' ? 'err' : 'ok'}">
                    <small>Alarm</small>
                    <strong>${_alarmMode.toUpperCase().replace('_', ' ')}</strong>
                </div>
            `;
        }
        const chip = $('securityPosture');
        if (chip) {
            const armed = _alarmMode !== 'disarmed';
            chip.textContent = armed ? 'armed' : 'monitoring';
            chip.className = 'state-chip ' + (armed ? 'state-warn' : 'state-ok');
        }

        // Locks list
        const lockList = $('secLocksList');
        if (lockList) {
            const locks = entities.filter((e) => e.domain === 'lock');
            lockList.innerHTML = locks.map((l) => `
                <div class="entity-row" data-entity-click="${l.entity_id}">
                    <span class="tile-icon lock" style="width:32px;height:32px;"><svg class="mdi" viewBox="0 0 24 24"><path d="M18 8h-1V6a5 5 0 0 0-10 0v2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2zM9 6a3 3 0 0 1 6 0v2H9z"/></svg></span>
                    <div>
                        <strong>${l.name}</strong>
                        <small>${l.entity_id} · ${l.state || 'unknown'}${l.user_override ? ' · override' : ''}</small>
                    </div>
                </div>
            `).join('') || '<p class="muted">No locks configured.</p>';
        }

        // Motion / occupancy
        const motionList = $('secMotionList');
        if (motionList) {
            const sensors = entities.filter((e) => e.device_class === 'motion' || e.device_class === 'occupancy');
            motionList.innerHTML = sensors.map((s) => `
                <div class="entity-row" data-entity-click="${s.entity_id}">
                    <span class="tile-icon motion ${s.state === 'on' ? 'active' : ''}" style="width:32px;height:32px;"><svg class="mdi" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/></svg></span>
                    <div>
                        <strong>${s.name}</strong>
                        <small>${s.entity_id} · ${s.state}${s.last_changed ? ' · ' + new Date(s.last_changed).toLocaleTimeString() : ''}</small>
                    </div>
                </div>
            `).join('') || '<p class="muted">No motion sensors.</p>';
        }

        // Events list (filtered audit + logbook for security-relevant items)
        try {
            const audit = await api('/api/v2/system/audit-log');
            const security = (audit.entries || [])
                .filter((e) => /lock|unlock|alarm|automation|integration|attacker/i.test(e.event + ' ' + (e.actor || '')))
                .slice(0, 20);
            const eventsHost = $('secEventsList');
            if (eventsHost) {
                eventsHost.innerHTML = security.map((e) => `
                    <div class="activity">
                        <time>${new Date(e.ts).toLocaleTimeString()}</time>
                        <div><strong>${e.actor}</strong><span>${e.event} ${e.detail ? JSON.stringify(e.detail) : ''}</span></div>
                    </div>
                `).join('') || '<p class="muted">No security events yet.</p>';
            }
        } catch (e) { /* audit log may be gated */ }

        // Alarm mode element refresh
        const alarm = $('alarmMode');
        if (alarm) {
            alarm.className = 'alarm-mode';
            if (_alarmMode === 'armed_home') alarm.classList.add('armed-home');
            if (_alarmMode === 'armed_away') alarm.classList.add('armed-away');
            alarm.textContent = _alarmMode.toUpperCase().replace('_', ' ');
        }

        // People
        try {
            const peopleResp = await api('/api/v2/config/people');
            const peopleList = $('secPeopleList');
            if (peopleList) {
                peopleList.innerHTML = (peopleResp.people || []).map((p) => `
                    <div class="entity-row">
                        <span class="avatar-circle" style="width:32px;height:32px;font-size:.85rem">${(p.name || 'P')[0]}</span>
                        <div>
                            <strong>${p.name}</strong>
                            <small>${p.role} · last seen ${new Date(p.last_seen).toLocaleString()}</small>
                        </div>
                    </div>
                `).join('');
            }
        } catch (e) { /* ignore */ }
    }

    function setAlarmMode(mode) {
        _alarmMode = mode;
        loadSecurityDashboard();
        const entry = { time: new Date().toTimeString().slice(0, 5), source: 'Alarm panel', message: `Mode changed to ${mode.replace('_', ' ')}` };
        // piggy-back on logbook DOM
        const logbook = $('activityList');
        if (logbook) {
            const el = document.createElement('div');
            el.className = 'activity';
            el.innerHTML = `<time>${entry.time}</time><div><strong>${entry.source}</strong><span>${entry.message}</span></div>`;
            logbook.insertBefore(el, logbook.firstChild);
        }
    }

    async function loadNetworkDashboard() {
        try {
            const [net, topo] = await Promise.all([
                api('/api/v2/zigbee/network'),
                api('/api/v2/zigbee/topology'),
            ]);

            $('netCoordInfo').innerHTML = `
                <div><span>PAN ID</span><strong>${net.pan_id}</strong></div>
                <div><span>Channel</span><strong>${net.channel}</strong></div>
                <div><span>Coordinator</span><strong>${net.coordinator}</strong></div>
                <div><span>Permit join</span><strong>${net.permit_join ? 'yes' : 'no'}</strong></div>
                <div><span>Firmware</span><strong>${net.coordinator_firmware}</strong></div>
                <div><span>Packets seen</span><strong>${net.packets_total}</strong></div>
            `;

            const routers = topo.nodes.filter((n) => n.role === 'router').length;
            const endDev = topo.nodes.filter((n) => n.role === 'end_device').length;
            const avgLqi = Math.round(topo.nodes.filter((n) => n.role !== 'coordinator').reduce((a, n) => a + n.lqi, 0) / Math.max(1, topo.nodes.length - 1));
            const minLqi = Math.min(...topo.nodes.filter((n) => n.role !== 'coordinator').map((n) => n.lqi));
            $('meshHealth').innerHTML = `
                <div class="metric ${avgLqi > 160 ? 'ok' : 'warn'}"><strong>${avgLqi}</strong><small>avg LQI</small></div>
                <div class="metric ${minLqi > 130 ? 'ok' : 'warn'}"><strong>${minLqi}</strong><small>min LQI</small></div>
                <div class="metric ok"><strong>${routers}</strong><small>routers</small></div>
                <div class="metric ok"><strong>${endDev}</strong><small>end devices</small></div>
            `;

            const rateLabel = $('netPacketRateLabel');
            if (rateLabel) rateLabel.textContent = `${net.packets_per_second || 0} pps`;
            // Simple sparkline using the in-browser rolling buffer
            if (!HA._netPacketBuffer) HA._netPacketBuffer = [];
            HA._netPacketBuffer.push(net.packets_per_second || 0);
            if (HA._netPacketBuffer.length > 20) HA._netPacketBuffer.shift();
            HA.charts.renderLineChart($('netPacketChart'), HA._netPacketBuffer, { color: '#03a9f4' });

            $('netDevicesGrid').innerHTML = topo.nodes.map((n) => {
                const lqiPct = Math.round((n.lqi / 255) * 100);
                const lqiClass = n.lqi > 160 ? '' : n.lqi > 120 ? 'mid' : 'low';
                return `
                    <div class="net-device-card" data-nwk="${n.nwk}">
                        <div class="nwk">${n.nwk}</div>
                        <strong>${n.name}</strong>
                        <span class="role ${n.role}">${n.role}</span>
                        <div class="stats">
                            <span>LQI ${n.lqi}</span>
                            <span>${typeof n.battery === 'number' ? n.battery + '%' : n.battery}</span>
                            <span>${n.model || ''}</span>
                        </div>
                        <div class="lqi-bar"><div class="lqi-fill ${lqiClass}" style="width:${lqiPct}%"></div></div>
                    </div>
                `;
            }).join('');

            // Secondary mesh map (different container than /view-map)
            HA.meshMap.render(topo, 'netMeshMap', 'netNodeDetail');
        } catch (e) {
            console.error('network dashboard', e);
        }
    }

    function refreshActiveDashboard() {
        const active = document.querySelector('#view-overview .dashboard-panel.active');
        if (!active) return;
        const name = active.dataset.dashboard;
        if (name === 'security') loadSecurityDashboard();
        else if (name === 'network') loadNetworkDashboard();
    }

    async function loadMap() {
        const topo = await api('/api/v2/zigbee/topology');
        HA.meshMap.render(topo);
    }

    async function loadZigbee() {
        const [net, pkts] = await Promise.all([
            api('/api/v2/zigbee/network'),
            api('/api/v2/zigbee/packets?limit=50'),
        ]);
        $('coordinatorInfo').innerHTML = `
            <div><span>PAN ID</span><strong>${net.pan_id}</strong></div>
            <div><span>Channel</span><strong>${net.channel}</strong></div>
            <div><span>Coordinator</span><strong>${net.coordinator}</strong></div>
            <div><span>Permit join</span><strong>${net.permit_join ? 'yes' : 'no'}</strong></div>
            <div><span>Firmware</span><strong>${net.coordinator_firmware}</strong></div>
            <div><span>Packets seen</span><strong>${net.packets_total}</strong></div>
            <div><span>Packets/s</span><strong>${net.packets_per_second}</strong></div>
        `;
        HA.zigbeeConsole.clear();
        (pkts.packets || []).slice(-80).forEach((p) => HA.zigbeeConsole.append(p));
        $('captureMeta').textContent = `capture.pcap · IEEE 802.15.4 · PAN ${net.pan_id} · channel ${net.channel} · rolling 2h window`;
    }

    async function loadDeveloper() {
        await loadEntities();
        const host = $('devStateTable');
        if (!host) return;
        const header = `
            <div class="hdr">entity_id</div><div class="hdr">state</div><div class="hdr">unit</div><div class="hdr">attributes</div>
        `;
        const rows = Object.values(entityCache).map((e) => `
            <div title="${e.entity_id}">${e.entity_id}</div><div>${e.state}${e.user_override ? ' *' : ''}</div><div>${e.unit || ''}</div><div>${e.nwk || ''} ${e.area || ''}</div>
        `).join('');
        host.innerHTML = header + rows;
    }

    async function loadNotifications() {
        const data = await api('/api/v2/notifications');
        const host = $('notificationList');
        if (!host) return;
        host.innerHTML = (data.notifications || []).map((n) => `
            <div class="notif ${n.read ? 'read' : ''}" data-nid="${n.notification_id}">
                <div class="notif-icon">!</div>
                <div class="notif-body">
                    <strong>${n.title}</strong>
                    <small>${new Date(n.created_at).toLocaleString()} · ${n.author || 'system'} · ${n.notification_id}</small>
                    <p>${n.message}</p>
                </div>
                <div class="notif-actions">
                    ${n.read ? '' : `<button class="ha-btn ghost" type="button" data-read="${n.notification_id}">Mark read</button>`}
                    <button class="ha-btn ghost" type="button" data-dismiss="${n.notification_id}">Dismiss</button>
                </div>
            </div>
        `).join('') || '<p class="muted">No persistent notifications.</p>';
        host.querySelectorAll('[data-dismiss]').forEach((btn) => btn.addEventListener('click', async (ev) => {
            await api(`/api/v2/notifications/${ev.target.dataset.dismiss}`, { method: 'DELETE' });
            loadNotifications();
        }));
        host.querySelectorAll('[data-read]').forEach((btn) => btn.addEventListener('click', async (ev) => {
            await api(`/api/v2/notifications/${ev.target.dataset.read}/read`, { method: 'POST', body: '{}' });
            loadNotifications();
        }));

        // Add "new" button in the header if not present
        const header = host.closest('.hui-card')?.querySelector('header');
        if (header && !header.querySelector('.notif-new-btn')) {
            const btn = document.createElement('button');
            btn.className = 'ha-btn notif-new-btn';
            btn.type = 'button';
            btn.textContent = '+ New';
            btn.addEventListener('click', newNotificationDialog);
            header.appendChild(btn);
        }
        updateNotifBadge(data.notifications || []);
    }

    function updateNotifBadge(notifs) {
        const unread = notifs.filter((n) => !n.read).length;
        const badge = $('notifBadge'); const dot = $('notifDot');
        if (unread) { badge?.classList.add('on'); dot?.classList.add('on'); }
        else { badge?.classList.remove('on'); dot?.classList.remove('on'); }
    }

    function newNotificationDialog() {
        const title = prompt('Notification title:');
        if (!title) return;
        const message = prompt('Notification message:') || '';
        api('/api/v2/notifications', { method: 'POST', body: JSON.stringify({ title, message }) })
            .then(() => { HA.toast('Notification created', 'ok'); loadNotifications(); })
            .catch((e) => HA.toast(e.message, 'err'));
    }

    // ------------------ MORE-INFO DIALOG ------------------
    async function openMoreInfo(entityId) {
        try {
            const data = await api(`/api/v2/states/${encodeURIComponent(entityId)}`);
            const entity = data.entity;
            const history = data.history || [];
            $('moreInfoTitle').textContent = entity.name || entity.entity_id;
            const body = $('moreInfoBody');
            const role = getCurrentRole();
            const canControl = role === 'owner' || role === 'user';

            let controls = '';
            const isHardwareSecured = entity.entity_id === 'lock.main_door_smart_lock';

            if (entity.domain === 'lock' && isHardwareSecured) {
                // Main Door Smart Lock is hardware-secured. The UI is
                // intentionally read-only: only the mesh coordinator
                // can operate it, and only with a valid PIN.
                controls = `
                    <div class="more-info-controls">
                        <button class="ha-btn" disabled title="Hardware-secured, coordinator-only">Lock</button>
                        <button class="ha-btn ghost" disabled title="Hardware-secured, coordinator-only">Unlock</button>
                    </div>
                    <p class="muted">Managed by the mesh coordinator. Physical PIN required; this panel is read-only.</p>
                `;
            } else if (entity.domain === 'lock' && canControl) {
                controls = `
                    <div class="more-info-controls">
                        <button class="ha-btn ${entity.state === 'locked' ? '' : 'ghost'}" data-call="lock:lock:${entity.entity_id}">Lock</button>
                        <button class="ha-btn ${entity.state === 'unlocked' ? 'danger' : 'ghost'}" data-call="lock:unlock:${entity.entity_id}">Unlock</button>
                    </div>
                `;
            } else if ((entity.domain === 'switch' || entity.domain === 'light') && canControl) {
                controls = `
                    <div class="more-info-controls">
                        <button class="ha-btn" data-call="${entity.domain}:turn_on:${entity.entity_id}">Turn on</button>
                        <button class="ha-btn ghost" data-call="${entity.domain}:turn_off:${entity.entity_id}">Turn off</button>
                        <button class="ha-btn ghost" data-call="${entity.domain}:toggle:${entity.entity_id}">Toggle</button>
                    </div>
                `;
            } else if (entity.domain === 'binary_sensor' || entity.domain === 'sensor') {
                controls = `<p class="muted">Read-only ${entity.domain}. Last changed ${new Date(entity.last_changed).toLocaleString()}.</p>`;
            }

            const sparklineValues = history.map((p) => p.value);
            body.innerHTML = `
                <div class="more-info-head">
                    <span class="tile-icon ${entityIcon(entity.entity_id)}" style="width:48px;height:48px;"><svg class="mdi" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/></svg></span>
                    <div>
                        <div class="more-info-state">${stateLabel(entity)}</div>
                        <div class="muted">${entity.entity_id}</div>
                    </div>
                </div>
                ${controls}
                ${sparklineValues.length ? `<div class="more-info-chart" id="moreInfoChart"></div>` : ''}
                <h3 class="muted" style="margin-top:12px;font-size:.8rem;text-transform:uppercase;letter-spacing:.5px">Attributes</h3>
                <dl class="attr-list">
                    ${Object.entries(entity).filter(([k]) => !['entity_id','name','state','user_override','overridden_by','last_changed'].includes(k)).map(([k, v]) => `<dt>${k}</dt><dd>${typeof v === 'object' ? JSON.stringify(v) : v}</dd>`).join('')}
                    ${entity.user_override ? `<dt>override_by</dt><dd>${entity.overridden_by}</dd>` : ''}
                    <dt>last_changed</dt><dd>${new Date(entity.last_changed).toLocaleString()}</dd>
                </dl>
                ${entity.user_override && role === 'owner' ? `<button class="ha-btn ghost" type="button" id="clearOverrideBtn">Clear manual override</button>` : ''}
            `;

            if (sparklineValues.length) {
                setTimeout(() => HA.charts.renderLineChart($('moreInfoChart'), history, { color: '#03a9f4' }), 30);
            }

            body.querySelectorAll('[data-call]').forEach((btn) => btn.addEventListener('click', async () => {
                const [domain, service, eid] = btn.dataset.call.split(':');
                btn.disabled = true;
                try {
                    await api(`/api/v2/services/${domain}/${service}`, { method: 'POST', body: JSON.stringify({ entity_id: eid }) });
                    HA.toast(`${service} executed on ${eid}`, 'ok');
                    await loadEntities();
                    openMoreInfo(eid); // refresh dialog
                } catch (e) {
                    HA.toast(e.message, 'err');
                } finally { btn.disabled = false; }
            }));

            $('clearOverrideBtn')?.addEventListener('click', async () => {
                // We don't expose direct override clear; call turn_off/lock to reset to something sensible
                HA.toast('Use a service call to reset the state', '');
            });

            $('moreInfoDialog').showModal();
        } catch (e) {
            HA.toast(`Cannot load entity: ${e.message}`, 'err');
        }
    }

    function getCurrentRole() {
        try {
            const stored = JSON.parse(localStorage.getItem('ha_user') || '{}');
            return stored.role || 'user';
        } catch (e) { return 'user'; }
    }

    HA.views = {
        authedFetch, api,
        loadEntities, loadLogbook, loadHistory, loadEnergy,
        loadMap, loadZigbee, loadDeveloper, loadNotifications,
        renderOverviewMetrics, renderEntityList,
        loadSecurityDashboard, loadNetworkDashboard, refreshActiveDashboard, setAlarmMode,
        get alarmMode() { return _alarmMode; },
        openMoreInfo,
        getCurrentRole,
        entityCache,
    };
})();
