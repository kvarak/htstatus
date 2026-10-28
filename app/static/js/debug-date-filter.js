/**
 * Pure date-range and user filtering logic for the admin debug charts.
 * Loaded in the browser (window.DebugDateFilter) and by Node tests (module.exports).
 */
(function (root) {
    'use strict';

    const DEFAULT_MONTHS = 6;

    function parseDate(dateStr) {
        if (!dateStr || dateStr === 'N/A' || dateStr === '-') return null;
        const date = new Date(dateStr);
        return Number.isNaN(date.getTime()) ? null : date;
    }

    function formatDateForInput(date) {
        return date.toISOString().split('T')[0];
    }

    function defaultDateRange(now = new Date(), months = DEFAULT_MONTHS) {
        const start = new Date(now);
        start.setMonth(start.getMonth() - months);
        return { start, end: new Date(now) };
    }

    // End date is inclusive: a YYYY-MM-DD end covers that whole (UTC) day.
    function endOfDay(date) {
        const end = new Date(date);
        end.setUTCHours(23, 59, 59, 999);
        return end;
    }

    /**
     * Validate the two date input values.
     * Returns {start, end} on success or {error} with a user-facing message.
     */
    function validateDateRange(startStr, endStr) {
        if (!startStr || !endStr) {
            return { error: 'Please select both start and end dates.' };
        }
        const start = parseDate(startStr);
        const end = parseDate(endStr);
        if (!start || !end) {
            return { error: 'Please enter valid dates.' };
        }
        if (start > end) {
            return { error: 'Start date must be on or before end date.' };
        }
        return { start, end: endOfDay(end) };
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
        formatDateForInput,
        defaultDateRange,
        endOfDay,
        validateDateRange,
        filterUsersByDateRange,
        filterUsers,
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        root.DebugDateFilter = api;
    }
})(typeof window !== 'undefined' ? window : globalThis);
