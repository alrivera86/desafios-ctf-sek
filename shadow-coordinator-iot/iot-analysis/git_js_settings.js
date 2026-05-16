/**
 * Settings page with full CRUD. Each section has real create / edit / delete
 * backed by the /data/state.json persistence layer.  Role gating is enforced
 * on the server; the UI just adapts to hide buttons that wouldn't work.
 */
(function () {
    const HA = window.HA = window.HA || {};
    const $ = (id) => document.getElementById(id);
    let currentView = 'devices';

    function setTitle(title, desc) {
        $('settingsTitle').textContent = title;
        $('settingsDescription').textContent = desc;
    }

    function section(title, body, actions = '') {
        return `<section class="settings-section"><header class="section-header"><h3>${title}</h3>${actions}</header>${body}</section>`;
    }

    function action(act, target, label, cls = 'ghost') {
        return `<button class="ha-btn ${cls}" data-action="${act}" data-target="${target}" type="button">${label}</button>`;
    }

    function fmt(ts) {
        if (!ts) return '—';
        try { return new Date(ts).toLocaleString(); } catch (e) { return ts; }
    }

    function isOwner() { return HA.views.getCurrentRole() === 'owner'; }

    async function renderDevices() {
        setTitle('Devices & services', 'Manage integrations, devices, entities, helpers and repair issues.');
        const [integrations, repairs, info] = await Promise.all([
            HA.views.api('/api/v2/config/integrations'),
            HA.views.api('/api/v2/config/repairs'),
            HA.views.api('/api/v2/system/info'),
        ]);

        const intHtml = (integrations.integrations || []).map((i) => `
            <article class="integration-card">
                <div class="integration-icon ${i.domain}">${i.name[0]}</div>
                <div class="integration-meta">
                    <strong>${i.name}</strong>
                    <span>${i.status} · ${i.devices} devices · ${i.entities} entities · ${i.source}</span>
                </div>
                ${i.domain === 'notify' ? action('openNotify', i.domain, 'Configure', '')
                                         : action('reloadIntegration', i.domain, i.domain === 'file_editor' ? 'Open' : (isOwner() ? 'Configure' : 'View'))}
            </article>
        `).join('');

        const repHtml = (repairs.repairs || []).map((r) => `
            <div class="repair-item ${r.severity === 'warning' ? 'warn' : r.severity === 'error' ? 'err' : ''}">
                <strong>${r.title}</strong><span>${r.description}</span>
            </div>
        `).join('');

        const sysHtml = [
            ['Core', info.core],
            ['Supervisor', info.supervisor],
            ['Operating System', info.os],
            ['Gateway', info.gateway_model],
            ['Host', info.host],
            ['PAN ID', info.pan_id],
            ['Zigbee channel', info.zigbee_channel],
            ['Uptime', `${info.uptime_seconds}s`],
            ['Last backup', info.last_backup ? fmt(info.last_backup) : '—'],
        ].map(([label, value]) => `<div><span>${label}</span><strong>${value}</strong></div>`).join('');

        $('settingsContent').innerHTML =
            section('Configured integrations', `<div class="integration-grid">${intHtml}</div>`) +
            section('Repairs', `<div class="repair-list">${repHtml}</div>`) +
            section('System information', `<div class="system-grid">${sysHtml}</div>`) +
            section('Diagnostics', `
                <p class="muted">Zigbee diagnostics bundle (IEEE 802.15.4 pcap format).</p>
                <div class="button-row">
                    <a class="ha-btn" href="/diagnostics/capture.pcap" download>Download capture.pcap</a>
                    <button class="ha-btn ghost" type="button" id="regenCapture2">Regenerate</button>
                </div>
                <pre id="captureMeta2" class="mono">capture.pcap · IEEE 802.15.4 · channel ${info.zigbee_channel} · rolling 2h window</pre>
            `);

        wireActions();
    }

    async function renderAutomations() {
        setTitle('Automations & scenes', 'Create and manage automations, scripts, scenes and blueprints.');
        const data = await HA.views.api('/api/v2/config/automations');
        const html = (data.items || []).map((item) => `
            <div class="settings-item" data-auto-id="${item.id}">
                <div>
                    <strong>${item.name}</strong>
                    <span>${item.type} · <b>${item.state}</b> · last triggered ${fmt(item.last_triggered)}${item.trigger_time ? ' · schedule ' + item.trigger_time : ''}</span>
                </div>
                <div class="inline-actions">
                    ${item.type === 'automation' ? action('toggleAutomation', item.id, item.state === 'on' ? 'Turn off' : 'Turn on', item.state === 'on' ? 'ghost' : '') : action('triggerAutomation', item.id, 'Run')}
                    ${isOwner() ? action('editAutomation', item.id, 'Edit') : ''}
                    ${isOwner() ? action('deleteAutomation', item.id, 'Delete', 'ghost danger') : ''}
                </div>
            </div>
        `).join('');
        const createBtn = isOwner() ? `<button class="ha-btn" id="newAutomationBtn" type="button">+ New automation</button>` : '';
        $('settingsContent').innerHTML = section('Automations, scenes and scripts', `<div class="settings-list">${html}</div>`, createBtn);
        wireActions();
        $('newAutomationBtn')?.addEventListener('click', newAutomationDialog);
    }

    async function renderAreas() {
        setTitle('Areas, labels & zones', 'Organize devices by physical campus areas and zones.');
        const data = await HA.views.api('/api/v2/config/areas');
        const html = (data.areas || []).map((a) => `
            <article class="integration-card">
                <div class="integration-icon recorder">${a.name[0]}</div>
                <div class="integration-meta"><strong>${a.name}</strong><span>${a.floor} · ${a.devices} devices · ${a.entities} entities</span></div>
                <div class="inline-actions">
                    ${action('reloadArea', a.id, 'Refresh')}
                    ${isOwner() ? action('editArea', a.id, 'Edit') : ''}
                    ${isOwner() ? action('deleteArea', a.id, 'Delete', 'ghost danger') : ''}
                </div>
            </article>
        `).join('');
        const create = isOwner() ? `<button class="ha-btn" id="newAreaBtn" type="button">+ New area</button>` : '';
        $('settingsContent').innerHTML =
            section('Areas', `<div class="integration-grid">${html}</div>`, create) +
            section('Zones', `
                <div class="settings-list">
                    <div class="settings-item"><div><strong>Campus perimeter</strong><span>radius 140 m · passive tracking</span></div>${action('callService', 'zone_reload', 'Reload')}</div>
                    <div class="settings-item"><div><strong>Facilities office</strong><span>radius 35 m · admin presence</span></div>${action('callService', 'zone_facilities', 'Edit')}</div>
                </div>
            `);
        wireActions();
        $('newAreaBtn')?.addEventListener('click', newAreaDialog);
    }

    async function renderVoice() {
        setTitle('Voice assistants', 'Configure Assist pipelines and voice satellites.');
        const data = await HA.views.api('/api/v2/config/voice-assistants');
        const html = (data.pipelines || []).map((p) => `
            <div class="settings-item" data-vp-id="${p.id}">
                <div><strong>${p.name}</strong><span>${p.language} · wake word ${p.wake_word} · ${p.status}${p.enabled ? '' : ' (disabled)'}</span></div>
                <div class="inline-actions">
                    ${action('testVoice', p.id, 'Test')}
                    ${isOwner() ? action('toggleVoice', p.id, p.enabled ? 'Disable' : 'Enable') : ''}
                    ${isOwner() ? action('editVoice', p.id, 'Edit') : ''}
                </div>
            </div>
        `).join('');
        $('settingsContent').innerHTML = section('Assist pipelines', `<div class="settings-list">${html}</div>`);
        wireActions();
    }

    async function renderDashboards() {
        setTitle('Dashboards', 'Manage Lovelace dashboards, resources and views.');
        const data = await HA.views.api('/api/v2/config/dashboards');
        const html = (data.dashboards || []).map((d) => `
            <div class="settings-item">
                <div><strong>${d.name}</strong><span>${d.url} · ${d.views} views · ${d.mode}${d.visible ? '' : ' · hidden'}</span></div>
                <div class="inline-actions">
                    ${action('reloadDashboard', d.id, 'Reload')}
                    ${isOwner() && d.id !== 'lovelace' ? action('toggleDashboard', d.id, d.visible ? 'Hide' : 'Show') : ''}
                    ${isOwner() && d.id !== 'lovelace' ? action('deleteDashboard', d.id, 'Delete', 'ghost danger') : ''}
                </div>
            </div>
        `).join('');
        const create = isOwner() ? `<button class="ha-btn" id="newDashBtn" type="button">+ New dashboard</button>` : '';
        $('settingsContent').innerHTML = section('Dashboards', `<div class="settings-list">${html}</div>`, create);
        wireActions();
        $('newDashBtn')?.addEventListener('click', newDashboardDialog);
    }

    async function renderPeople() {
        setTitle('People', 'Manage users, persons and tracked devices.');
        const data = await HA.views.api('/api/v2/config/people');
        const html = (data.people || []).map((p) => `
            <div class="settings-item">
                <div><strong>${p.name}</strong><span>${p.role} · ${p.devices} devices · last seen ${fmt(p.last_seen)}</span></div>
                <div class="inline-actions">
                    ${action('refreshPerson', p.id, 'Refresh')}
                    ${isOwner() ? action('editPerson', p.id, 'Edit') : ''}
                    ${isOwner() && p.id !== 'admin' ? action('deletePerson', p.id, 'Delete', 'ghost danger') : ''}
                </div>
            </div>
        `).join('');
        const create = isOwner() ? `<button class="ha-btn" id="newPersonBtn" type="button">+ New person</button>` : '';
        $('settingsContent').innerHTML = section('People', `<div class="settings-list">${html}</div>`, create);
        wireActions();
        $('newPersonBtn')?.addEventListener('click', newPersonDialog);
    }

    async function renderSystem() {
        setTitle('System', 'Updates, backups, storage, network and hardware information.');
        const [info, options, backups] = await Promise.all([
            HA.views.api('/api/v2/system/info'),
            HA.views.api('/api/v2/config/system-options'),
            HA.views.api('/api/v2/config/backups'),
        ]);
        const updates = (options.updates || []).map((u) => `
            <div class="settings-item"><div><strong>${u.component}</strong><span>installed ${u.installed} · available ${u.available}</span></div>${action('callService', 'update_' + u.component, 'Check')}</div>
        `).join('');
        const network = [
            ['Hostname', options.network.hostname],
            ['IPv4 method', options.network.ipv4_method],
            ['DNS', options.network.dns.join(', ')],
            ['Host', info.host],
            ['Gateway', info.gateway_model],
            ['Uptime', `${info.uptime_seconds}s`],
        ].map(([l, v]) => `<div><span>${l}</span><strong>${v}</strong></div>`).join('');

        const backupRows = (backups.backups || []).map((b) => `
            <div class="settings-item">
                <div><strong>${b.id}</strong><span>${fmt(b.created_at)} · ${b.size_mb} MB · ${b.type || 'auto'} · ${b.note || ''}</span></div>
                <div class="inline-actions">
                    ${action('restoreBackup', b.id, 'Restore')}
                    ${isOwner() ? action('deleteBackup', b.id, 'Delete', 'ghost danger') : ''}
                </div>
            </div>
        `).join('');

        $('settingsContent').innerHTML =
            section('Updates', `<div class="settings-list">${updates}</div>`) +
            section('Network', `<div class="system-grid">${network}</div>`, isOwner() ? `<button class="ha-btn ghost" id="editNetworkBtn" type="button">Edit</button>` : '') +
            section('Backups', `<div class="settings-list">${backupRows}</div>`, isOwner() ? `<button class="ha-btn" id="newBackupBtn" type="button">Create backup</button>` : '') +
            section('Advanced', `
                <div class="button-row">
                    ${action('callService', 'homeassistant.restart', 'Restart Home Assistant')}
                    ${action('callService', 'homeassistant.check_config', 'Check configuration')}
                    ${isOwner() ? `<button class="ha-btn ghost" id="viewAuditLogBtn" type="button">View audit log</button>` : ''}
                </div>
            `);

        $('newBackupBtn')?.addEventListener('click', async () => {
            const note = prompt('Backup note (optional):') || '';
            try {
                const r = await HA.views.api('/api/v2/config/backups', { method: 'POST', body: JSON.stringify({ note }) });
                HA.toast(`Backup ${r.backup.id} created`, 'ok');
                renderSystem();
            } catch (e) { HA.toast(e.message, 'err'); }
        });
        $('editNetworkBtn')?.addEventListener('click', editNetworkDialog);
        $('viewAuditLogBtn')?.addEventListener('click', showAuditLog);
        wireActions();
    }

    async function render(view) {
        currentView = view || currentView;
        document.querySelectorAll('.settings-menu button').forEach((b) => b.classList.toggle('selected', b.dataset.settings === currentView));
        const map = {
            devices: renderDevices, automations: renderAutomations, areas: renderAreas,
            voice: renderVoice, dashboards: renderDashboards, people: renderPeople, system: renderSystem,
        };
        await (map[currentView] || renderDevices)();
    }

    // ---------------- dialogs ----------------
    function newAutomationDialog() {
        const name = prompt('Automation name:');
        if (!name) return;
        const time = prompt('Trigger time (HH:MM):', '08:00') || '08:00';
        HA.views.api('/api/v2/config/automations', { method: 'POST', body: JSON.stringify({ name, trigger_time: time }) })
            .then(() => { HA.toast('Automation created', 'ok'); render(); })
            .catch((e) => HA.toast(e.message, 'err'));
    }

    async function editAutomationDialog(id) {
        const items = (await HA.views.api('/api/v2/config/automations')).items;
        const item = items.find((a) => a.id === id);
        if (!item) return;
        const name = prompt('Rename automation:', item.name);
        if (name === null) return;
        const time = prompt('Trigger time:', item.trigger_time || '08:00');
        if (time === null) return;
        try {
            await HA.views.api(`/api/v2/config/automations/${id}`, { method: 'PATCH', body: JSON.stringify({ name, trigger_time: time }) });
            HA.toast('Automation updated', 'ok'); render();
        } catch (e) { HA.toast(e.message, 'err'); }
    }

    function newAreaDialog() {
        const name = prompt('Area name:'); if (!name) return;
        const floor = prompt('Floor:', '1st floor') || '1st floor';
        HA.views.api('/api/v2/config/areas', { method: 'POST', body: JSON.stringify({ name, floor }) })
            .then(() => { HA.toast('Area created', 'ok'); render(); })
            .catch((e) => HA.toast(e.message, 'err'));
    }

    async function editAreaDialog(id) {
        const areas = (await HA.views.api('/api/v2/config/areas')).areas;
        const item = areas.find((a) => a.id === id);
        if (!item) return;
        const name = prompt('Rename area:', item.name); if (name === null) return;
        const floor = prompt('Floor:', item.floor); if (floor === null) return;
        try {
            await HA.views.api(`/api/v2/config/areas/${id}`, { method: 'PATCH', body: JSON.stringify({ name, floor }) });
            HA.toast('Area updated', 'ok'); render();
        } catch (e) { HA.toast(e.message, 'err'); }
    }

    function newPersonDialog() {
        const name = prompt('Person name:'); if (!name) return;
        const role = prompt('Role (owner / user / local access):', 'user') || 'user';
        HA.views.api('/api/v2/config/people', { method: 'POST', body: JSON.stringify({ name, role }) })
            .then(() => { HA.toast('Person added', 'ok'); render(); })
            .catch((e) => HA.toast(e.message, 'err'));
    }

    async function editPersonDialog(id) {
        const people = (await HA.views.api('/api/v2/config/people')).people;
        const p = people.find((x) => x.id === id); if (!p) return;
        const name = prompt('Rename person:', p.name); if (name === null) return;
        const role = prompt('Role:', p.role); if (role === null) return;
        try {
            await HA.views.api(`/api/v2/config/people/${id}`, { method: 'PATCH', body: JSON.stringify({ name, role }) });
            HA.toast('Person updated', 'ok'); render();
        } catch (e) { HA.toast(e.message, 'err'); }
    }

    function newDashboardDialog() {
        const name = prompt('Dashboard name:'); if (!name) return;
        const url = prompt('URL path:', '/lovelace/' + name.toLowerCase().replace(/\s+/g, '_')) || '';
        if (!url) return;
        HA.views.api('/api/v2/config/dashboards', { method: 'POST', body: JSON.stringify({ name, url }) })
            .then(() => { HA.toast('Dashboard created', 'ok'); render(); })
            .catch((e) => HA.toast(e.message, 'err'));
    }

    async function editVoiceDialog(id) {
        const pipes = (await HA.views.api('/api/v2/config/voice-assistants')).pipelines;
        const p = pipes.find((x) => x.id === id); if (!p) return;
        const name = prompt('Rename pipeline:', p.name); if (name === null) return;
        const language = prompt('Language (e.g. es-CL):', p.language); if (language === null) return;
        const wake_word = prompt('Wake word (or disabled):', p.wake_word); if (wake_word === null) return;
        try {
            await HA.views.api(`/api/v2/config/voice-assistants/${id}`, { method: 'PATCH', body: JSON.stringify({ name, language, wake_word }) });
            HA.toast('Pipeline updated', 'ok'); render();
        } catch (e) { HA.toast(e.message, 'err'); }
    }

    async function editNetworkDialog() {
        const current = await HA.views.api('/api/v2/config/system-options');
        const hostname = prompt('Hostname:', current.network.hostname); if (hostname === null) return;
        const dns = prompt('DNS servers (comma separated):', current.network.dns.join(',')); if (dns === null) return;
        try {
            await HA.views.api('/api/v2/config/system-options', {
                method: 'PATCH',
                body: JSON.stringify({ hostname, dns: dns.split(',').map((s) => s.trim()).filter(Boolean) }),
            });
            HA.toast('Network configuration updated', 'ok'); render();
        } catch (e) { HA.toast(e.message, 'err'); }
    }

    async function showAuditLog() {
        try {
            const data = await HA.views.api('/api/v2/system/audit-log');
            const dialog = $('serviceConfigDialog');
            $('serviceDialogTitle').textContent = 'Audit log';
            $('serviceDialogBody').innerHTML = `<div class="audit-list">${(data.entries || []).map((e) => `
                <div class="audit-row"><time>${new Date(e.ts).toLocaleTimeString()}</time><span class="pill">${e.actor}</span><code>${e.event}</code><small>${JSON.stringify(e.detail)}</small></div>
            `).join('') || '<p class="muted">No events yet.</p>'}</div>`;
            dialog.showModal();
        } catch (e) { HA.toast(e.message, 'err'); }
    }

    function wireActions() {
        document.querySelectorAll('[data-action]').forEach((btn) => btn.addEventListener('click', async () => {
            const actionName = btn.dataset.action;
            const target = btn.dataset.target;
            if (actionName === 'openNotify') return openNotifyDialog();
            if (actionName === 'editAutomation') return editAutomationDialog(target);
            if (actionName === 'editArea') return editAreaDialog(target);
            if (actionName === 'editPerson') return editPersonDialog(target);
            if (actionName === 'editVoice') return editVoiceDialog(target);

            btn.disabled = true;
            const original = btn.textContent;
            btn.textContent = '…';
            try {
                if (actionName === 'reloadIntegration') {
                    await HA.views.api(`/api/v2/config/integrations/${target}/reload`, { method: 'POST', body: '{}' });
                    HA.toast(`Integration ${target} reloaded`, 'ok');
                } else if (actionName === 'toggleAutomation') {
                    await HA.views.api(`/api/v2/config/automations/${target}/toggle`, { method: 'POST', body: '{}' });
                    HA.toast('Automation toggled', 'ok');
                } else if (actionName === 'triggerAutomation') {
                    await HA.views.api(`/api/v2/config/automations/${target}/trigger`, { method: 'POST', body: '{}' });
                    HA.toast('Ran', 'ok');
                } else if (actionName === 'deleteAutomation') {
                    if (!confirm('Delete automation?')) { btn.disabled = false; btn.textContent = original; return; }
                    await HA.views.api(`/api/v2/config/automations/${target}`, { method: 'DELETE' });
                    HA.toast('Automation deleted', 'ok');
                } else if (actionName === 'reloadArea') {
                    await HA.views.api(`/api/v2/config/areas/${target}/reload`, { method: 'POST', body: '{}' });
                    HA.toast('Area refreshed', 'ok');
                } else if (actionName === 'deleteArea') {
                    if (!confirm('Delete area?')) { btn.disabled = false; btn.textContent = original; return; }
                    await HA.views.api(`/api/v2/config/areas/${target}`, { method: 'DELETE' });
                    HA.toast('Area deleted', 'ok');
                } else if (actionName === 'testVoice') {
                    await HA.views.api(`/api/v2/config/voice-assistants/${target}/test`, { method: 'POST', body: '{}' });
                    HA.toast('Pipeline tested OK', 'ok');
                } else if (actionName === 'toggleVoice') {
                    const pipes = (await HA.views.api('/api/v2/config/voice-assistants')).pipelines;
                    const p = pipes.find((x) => x.id === target);
                    await HA.views.api(`/api/v2/config/voice-assistants/${target}`, { method: 'PATCH', body: JSON.stringify({ enabled: !p.enabled }) });
                    HA.toast('Pipeline updated', 'ok');
                } else if (actionName === 'reloadDashboard') {
                    await HA.views.api(`/api/v2/config/dashboards/${target}/reload`, { method: 'POST', body: '{}' });
                    HA.toast('Dashboard reloaded', 'ok');
                } else if (actionName === 'toggleDashboard') {
                    const dashes = (await HA.views.api('/api/v2/config/dashboards')).dashboards;
                    const d = dashes.find((x) => x.id === target);
                    await HA.views.api(`/api/v2/config/dashboards/${target}`, { method: 'PATCH', body: JSON.stringify({ visible: !d.visible }) });
                    HA.toast('Dashboard updated', 'ok');
                } else if (actionName === 'deleteDashboard') {
                    if (!confirm('Delete dashboard?')) { btn.disabled = false; btn.textContent = original; return; }
                    await HA.views.api(`/api/v2/config/dashboards/${target}`, { method: 'DELETE' });
                    HA.toast('Dashboard deleted', 'ok');
                } else if (actionName === 'refreshPerson') {
                    await HA.views.api(`/api/v2/config/people/${target}/refresh`, { method: 'POST', body: '{}' });
                    HA.toast('Person refreshed', 'ok');
                } else if (actionName === 'deletePerson') {
                    if (!confirm('Delete person?')) { btn.disabled = false; btn.textContent = original; return; }
                    await HA.views.api(`/api/v2/config/people/${target}`, { method: 'DELETE' });
                    HA.toast('Person deleted', 'ok');
                } else if (actionName === 'deleteBackup') {
                    if (!confirm('Delete backup?')) { btn.disabled = false; btn.textContent = original; return; }
                    await HA.views.api(`/api/v2/config/backups/${target}`, { method: 'DELETE' });
                    HA.toast('Backup deleted', 'ok');
                } else if (actionName === 'restoreBackup') {
                    HA.toast(`Restore of ${target} scheduled`, 'ok');
                } else if (actionName === 'callService') {
                    // target may be "domain.service" or a bare key — default to system.noop
                    let [domain, svc] = target.includes('.') ? target.split('.') : ['system', target];
                    await HA.views.api(`/api/v2/services/${domain}/${svc}`, { method: 'POST', body: '{}' });
                    HA.toast(`${domain}.${svc}`, 'ok');
                }
            } catch (e) {
                HA.toast(e.message || 'Action failed', 'err');
            }
            btn.disabled = false; btn.textContent = original;
            setTimeout(() => render(), 300);
        }));

        $('regenCapture2')?.addEventListener('click', async () => {
            const btn = $('regenCapture2'); btn.disabled = true; btn.textContent = 'Regenerating…';
            try {
                const j = await HA.views.api('/api/v2/zigbee/capture/regenerate', { method: 'POST', body: '{}' });
                HA.toast(j.status === 'ok' ? 'capture.pcap regenerated' : 'Regeneration failed', j.status === 'ok' ? 'ok' : 'err');
            } catch (e) { HA.toast(e.message, 'err'); }
            btn.disabled = false; btn.textContent = 'Regenerate';
        });
    }

    function openNotifyDialog() {
        const dialog = $('serviceConfigDialog');
        $('serviceDialogTitle').textContent = 'Notifications · Enterprise alert bridge';
        $('serviceDialogBody').innerHTML = `
            <p class="muted">Configure notification targets used by automations, persistent notifications and repair alerts.</p>
            <div class="settings-item"><div><strong>persistent_notification</strong><span>Built-in</span></div></div>
            <div class="settings-item"><div><strong>notify.mobile_app_admin_phone</strong><span>Enabled</span></div></div>
            <div class="settings-item"><div><strong>notify.enterprise_alert_bridge</strong><span>Legacy connector · enabled</span></div></div>
            <label>notify.enterprise_alert_bridge · test URL</label>
            <input id="endpointUrl" type="text" placeholder="http://alerts.example.com/services/campus-gateway">
            <div class="button-row">
                <button class="ha-btn" id="testEndpoint" type="button">Call service</button>
                <button class="ha-btn ghost" type="button" id="testDefaultEndpoint">Use default</button>
            </div>
            <pre id="result">No test notification sent yet.</pre>
            <small class="muted">Legacy connector preserved for compatibility with the previous Python coordinator (/api/v2/system/notifications/test-endpoint).</small>
        `;
        dialog.showModal();

        $('testDefaultEndpoint').onclick = () => { $('endpointUrl').value = 'http://alerts.example.com/services/campus-gateway'; };
        $('testEndpoint').onclick = async () => {
            const endpointUrl = $('endpointUrl').value.trim();
            const result = $('result');
            if (!endpointUrl) { result.textContent = 'URL is required'; return; }
            result.textContent = 'Calling notify.enterprise_alert_bridge…';
            try {
                const resp = await fetch('/api/v2/system/notifications/test-endpoint', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ endpointUrl, domain: 'notify', service: 'enterprise_alert_bridge', message: 'Test notification' }),
                });
                const body = await resp.json().catch(() => ({ status: 'error', message: 'Unexpected response' }));
                result.textContent = JSON.stringify(body, null, 2);
            } catch (e) {
                result.textContent = JSON.stringify({ status: 'error', message: e.message }, null, 2);
            }
        };
    }

    HA.settings = { render, get currentView() { return currentView; } };
})();
