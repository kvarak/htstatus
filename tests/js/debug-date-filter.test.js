// Tests for app/static/js/debug-date-filter.js (run with: node --test tests/js/)
const test = require('node:test');
const assert = require('node:assert/strict');

const {
    DEFAULT_MONTHS,
    parseDate,
    presetDateRange,
    filterUsersByDateRange,
    filterUsers,
} = require('../../app/static/js/debug-date-filter.js');

const users = [
    { name: 'early', role: 'User', created: '2026-01-10T12:00:00Z' },
    { name: 'inRange', role: 'User', created: '2026-03-15T08:00:00Z' },
    { name: 'endDayEvening', role: 'User', created: '2026-04-30T21:30:00Z' },
    { name: 'admin', role: 'Admin', created: '2026-03-01T00:00:00Z' },
    { name: 'onlyUsage', role: 'User', last_usage: '2026-04-01T10:00:00Z' },
    { name: 'noDate', role: 'User', created: 'N/A' },
];

test('parseDate rejects placeholders and invalid strings', () => {
    for (const value of [null, undefined, '', 'N/A', '-', 'not a date']) {
        assert.equal(parseDate(value), null);
    }
    assert.equal(parseDate('2026-03-15').toISOString(), '2026-03-15T00:00:00.000Z');
});

test('presetDateRange goes the given number of months back without mutating now', () => {
    const now = new Date(2026, 9, 28, 12);
    const { start, end } = presetDateRange(3, now);
    assert.equal(start.getTime(), new Date(2026, 6, 28, 12).getTime());
    assert.equal(end.getTime(), now.getTime());
    assert.notEqual(end, now);
    assert.equal(now.getTime(), new Date(2026, 9, 28, 12).getTime());
});

test('presetDateRange "all" means no date filter', () => {
    assert.deepEqual(presetDateRange('all'), { start: null, end: null });
});

test('default time range is one year', () => {
    assert.equal(DEFAULT_MONTHS, 12);
});

test('filterUsersByDateRange keeps users inside the inclusive range', () => {
    const start = new Date('2026-03-01T00:00:00Z');
    const end = new Date('2026-04-30T23:59:59.999Z');
    const names = filterUsersByDateRange(users, start, end).map(u => u.name);
    assert.deepEqual(names, ['inRange', 'endDayEvening', 'admin', 'onlyUsage']);
});

test('filterUsersByDateRange returns all users when no range is set', () => {
    assert.equal(filterUsersByDateRange(users, null, null), users);
});

test('filterUsers combines admin hiding and date range', () => {
    const start = new Date('2026-03-01T00:00:00Z');
    const end = new Date('2026-04-30T23:59:59.999Z');
    const names = filterUsers(users, { hideAdmins: true, start, end }).map(u => u.name);
    assert.deepEqual(names, ['inRange', 'endDayEvening', 'onlyUsage']);
});

test('filterUsers with defaults returns everyone', () => {
    assert.equal(filterUsers(users).length, users.length);
});
