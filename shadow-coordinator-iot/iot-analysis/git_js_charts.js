/**
 * Minimal SVG chart helpers (line + area).
 * We avoid external libraries to keep the frontend trivially shippable.
 */
(function () {
    const HA = window.HA = window.HA || {};

    function buildPath(points, w, h, min, max) {
        if (!points.length) return '';
        const xStep = w / Math.max(1, points.length - 1);
        const range = max - min || 1;
        return points.map((p, i) => {
            const x = i * xStep;
            const y = h - ((p - min) / range) * h;
            return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
        }).join(' ');
    }

    function renderLineChart(host, values, { unit = '', color = '#03a9f4', area = true } = {}) {
        if (!host) return;
        const w = host.clientWidth || 400;
        const h = host.clientHeight || 200;
        const padL = 36, padB = 20, padT = 12, padR = 8;
        const cw = w - padL - padR;
        const ch = h - padB - padT;
        const numbers = values.map((p) => typeof p === 'object' ? p.value : p);
        const max = Math.max(...numbers) * 1.05;
        const min = Math.min(...numbers) * 0.95;
        const path = buildPath(numbers, cw, ch, min, max);
        const lines = 4;
        const gridLines = Array.from({ length: lines + 1 }).map((_, i) => {
            const y = (ch / lines) * i;
            const v = max - ((max - min) / lines) * i;
            return `<line class="chart-grid" x1="0" y1="${y}" x2="${cw}" y2="${y}"/><text class="axis-label" x="-8" y="${y + 4}" text-anchor="end">${v.toFixed(1)}</text>`;
        }).join('');
        const labels = values.length > 0 && typeof values[0] === 'object' ? values.filter((_, i) => i % Math.ceil(values.length / 6) === 0) : [];
        const xTicks = labels.map((p, idx) => {
            const origIndex = values.indexOf(p);
            const x = (cw / Math.max(1, values.length - 1)) * origIndex;
            const label = p.ts ? new Date(p.ts).getHours() + 'h' : idx;
            return `<text class="axis-label" x="${x}" y="${ch + 14}" text-anchor="middle">${label}</text>`;
        }).join('');
        host.innerHTML = `
            <svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
                <g transform="translate(${padL},${padT})">
                    ${gridLines}
                    ${area ? `<path class="chart-area" d="${path} L${cw},${ch} L0,${ch} Z"/>` : ''}
                    <path class="chart-line" style="stroke:${color}" d="${path}"/>
                    ${xTicks}
                </g>
            </svg>
        `;
    }

    function renderBarChart(host, values, { color = '#03a9f4' } = {}) {
        if (!host) return;
        const w = host.clientWidth || 400;
        const h = host.clientHeight || 200;
        const padL = 36, padB = 20, padT = 12, padR = 8;
        const cw = w - padL - padR;
        const ch = h - padB - padT;
        const max = Math.max(...values.map((v) => v.value)) * 1.1;
        const barWidth = cw / values.length * 0.65;
        const gap = cw / values.length * 0.35;
        const bars = values.map((v, i) => {
            const x = i * (barWidth + gap);
            const barH = Math.max(2, (v.value / max) * ch);
            return `
                <rect x="${x}" y="${ch - barH}" width="${barWidth}" height="${barH}" fill="${color}" rx="2"/>
                <text class="axis-label" x="${x + barWidth / 2}" y="${ch + 14}" text-anchor="middle">${v.label}</text>
                <text class="axis-label" x="${x + barWidth / 2}" y="${ch - barH - 4}" text-anchor="middle">${v.value.toFixed(0)}</text>
            `;
        }).join('');
        host.innerHTML = `
            <svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
                <g transform="translate(${padL},${padT})">
                    ${bars}
                </g>
            </svg>
        `;
    }

    HA.charts = { renderLineChart, renderBarChart };
})();
