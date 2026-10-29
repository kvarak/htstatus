// Tests for app/static/js/dark-mode.js with a minimal fake DOM (run with: node --test tests/js/)
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const SOURCE = fs.readFileSync(
    path.join(__dirname, '../../app/static/js/dark-mode.js'), 'utf8');

function setup({ stored = null, systemDark = false, startDark = false, charts = [] } = {}) {
    const classes = new Set(startDark ? ['dark-mode'] : []);
    const storage = new Map(stored === null ? [] : [['htstatus-dark-mode', stored]]);
    const listeners = {};
    let systemListener = null;
    const toggle = { addEventListener: (type, fn) => { listeners[type] = fn; } };
    const icon = { textContent: '' };
    const window = {
        matchMedia: () => ({
            matches: systemDark,
            addEventListener: (_type, fn) => { systemListener = fn; },
        }),
        Chart: {
            defaults: {},
            instances: Object.fromEntries(charts.map((c, i) => [i, c])),
        },
    };
    const context = {
        window,
        localStorage: {
            getItem: (k) => (storage.has(k) ? storage.get(k) : null),
            setItem: (k, v) => storage.set(k, v),
        },
        document: {
            documentElement: {
                classList: {
                    contains: (c) => classes.has(c),
                    toggle: (c, on) => (on ? classes.add(c) : classes.delete(c)),
                },
            },
            getElementById: (id) => ({ 'dark-mode-toggle': toggle, 'dark-mode-icon': icon }[id]),
            addEventListener: () => {},
        },
        Object,
    };
    vm.runInNewContext(SOURCE, context);
    return {
        isDark: () => classes.has('dark-mode'),
        icon,
        storage,
        click: () => listeners.click(),
        systemChange: (matches) => systemListener({ matches }),
        Chart: window.Chart,
    };
}

function fakeChart() {
    return {
        options: { scales: { x: {}, y: { ticks: { stepSize: 1 } } }, plugins: { legend: { labels: {} } } },
        updated: 0,
        update() { this.updated += 1; },
    };
}

test('shows the moon in light mode and the sun in dark mode', () => {
    assert.equal(setup().icon.textContent, '\uD83C\uDF19');
    assert.equal(setup({ startDark: true }).icon.textContent, '\u2600\uFE0F');
});

test('clicking toggles the mode and remembers the choice', () => {
    const page = setup();
    page.click();
    assert.equal(page.isDark(), true);
    assert.equal(page.storage.get('htstatus-dark-mode'), 'true');
    assert.equal(page.icon.textContent, '\u2600\uFE0F');
    page.click();
    assert.equal(page.isDark(), false);
    assert.equal(page.storage.get('htstatus-dark-mode'), 'false');
});

test('follows the system setting only until the user picks a mode', () => {
    const page = setup();
    page.systemChange(true);
    assert.equal(page.isDark(), true);

    const chosen = setup({ stored: 'false' });
    chosen.systemChange(true);
    assert.equal(chosen.isDark(), false);
});

test('sets Chart.js defaults and recolours existing charts on toggle', () => {
    const chart = fakeChart();
    const page = setup({ charts: [chart] });
    assert.equal(page.Chart.defaults.color, '#666');

    page.click();

    assert.equal(page.Chart.defaults.color, '#ced4da');
    assert.equal(chart.options.scales.y.ticks.color, '#ced4da');
    assert.equal(chart.options.scales.y.ticks.stepSize, 1);
    assert.equal(chart.options.scales.x.grid.color, 'rgba(255, 255, 255, 0.12)');
    assert.equal(chart.options.plugins.legend.labels.color, '#ced4da');
    assert.ok(chart.updated >= 2);
});
