// Tests for app/static/js/debug-date-filter.js (run with: node --test tests/js/)
const test = require('node:test');
const assert = require('node:assert/strict');

const {
    parseDate,
    formatDateForInput,
    defaultDateRange,
    endOfDay,
    validateDateRange,
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

test('formatDateForInput produces YYYY-MM-DD', () => {
    assert.equal(formatDateForInput(new Date('2026-10-28T19:00:00Z')), '2026-10-28');
});

test('defaultDateRange spans six months back from now without mutating it', () => {
    const now = new Date('2026-10-28T12:00:00Z');
    const { start, end } = defaultDateRange(now);
    assert.equal(formatDateForInput(start), '2026-04-28');
    assert.equal(end.getTime(), now.getTime());
    assert.notEqual(end, now);
    assert.equal(now.toISOString(), '2026-10-28T12:00:00.000Z');
});

test('validateDateRange requires both dates', () => {
    assert.match(validateDateRange('', '2026-01-01').error, /both start and end/);
    assert.match(validateDateRange('2026-01-01', '').error, /both start and end/);
});

test('validateDateRange rejects invalid and reversed ranges', () => {
    assert.match(validateDateRange('garbage', '2026-01-01').error, /valid dates/);
    assert.match(validateDateRange('2026-02-01', '2026-01-01').error, /on or before/);
});

test('validateDateRange allows a single day and makes the end inclusive', () => {
    const range = validateDateRange('2026-04-30', '2026-04-30');
    assert.equal(range.error, undefined);
    assert.equal(range.start.toISOString(), '2026-04-30T00:00:00.000Z');
    assert.equal(range.end.toISOString(), '2026-04-30T23:59:59.999Z');
});

test('endOfDay does not mutate its input', () => {
    const day = new Date('2026-04-30T00:00:00Z');
    endOfDay(day);
    assert.equal(day.toISOString(), '2026-04-30T00:00:00.000Z');
});

test('filterUsersByDateRange keeps users inside the inclusive range', () => {
    const { start, end } = validateDateRange('2026-03-01', '2026-04-30');
    const names = filterUsersByDateRange(users, start, end).map(u => u.name);
    assert.deepEqual(names, ['inRange', 'endDayEvening', 'admin', 'onlyUsage']);
});

test('filterUsersByDateRange returns all users when no range is set', () => {
    assert.equal(filterUsersByDateRange(users, null, null), users);
});

test('filterUsers combines admin hiding and date range', () => {
    const { start, end } = validateDateRange('2026-03-01', '2026-04-30');
    const names = filterUsers(users, { hideAdmins: true, start, end }).map(u => u.name);
    assert.deepEqual(names, ['inRange', 'endDayEvening', 'onlyUsage']);
});

test('filterUsers with defaults returns everyone', () => {
    assert.equal(filterUsers(users).length, users.length);
});
