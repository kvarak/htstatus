/**
 * Pure date-range and user filtering logic for the admin debug charts.
 * Loaded in the browser (window.DebugDateFilter) and by Node tests (module.exports).
 */
(function (root) {
    'use strict';

    const DEFAULT_MONTHS = 12;

    function parseDate(dateStr) {
        if (!dateStr || dateStr === 'N/A' || dateStr === '-') return null;
        const date = new Date(dateStr);
        return Number.isNaN(date.getTime()) ? null : date;
    }

    /**
     * Date range for a time range preset: a number of months back from now,
     * or "all" for no date filter ({start: null, end: null}).
     */
    function presetDateRange(months, now = new Date()) {
        if (months === 'all') return { start: null, end: null };
        const start = new Date(now);
        start.setMonth(start.getMonth() - months);
        return { start, end: new Date(now) };
    }

    function filterUsersByDateRange(users, start, end) {
        if (!start || !end) return users;
        return users.filter(user => {
            const userDate = parseDate(user.created || user.last_usage);
            return userDate !== null && userDate >= start && userDate <= end;
        });
    }

    function filterUsers(users, { hideAdmins = false, start = null, end = null } = {}) {
        const visible = hideAdmins ? users.filter(user => user.role !== 'Admin') : users;
        return filterUsersByDateRange(visible, start, end);
    }

    const api = {
        DEFAULT_MONTHS,
        parseDate,
        presetDateRange,
        filterUsersByDateRange,
        filterUsers,
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        root.DebugDateFilter = api;
    }
})(typeof window !== 'undefined' ? window : globalThis);
