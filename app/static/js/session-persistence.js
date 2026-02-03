/**
 * PWA Session Persistence Manager
 * Handles session storage for Progressive Web App to prevent re-login requirements
 */

class SessionPersistence {
    constructor() {
        this.isPWA = this.detectPWA();
        this.sessionKey = 'ht_session_data';
        this.restorationAttempts = 0;
        this.maxRestorationAttempts = 3;
        this.restorationInProgress = false;
        this.restorationTimeout = 10000; // 10 seconds
        this.init();
    }

    /**
     * Detect if running as PWA (installed app)
     */
    detectPWA() {
        // Check if running in standalone mode (PWA)
        return window.matchMedia('(display-mode: standalone)').matches ||
               window.navigator.standalone === true ||
               document.referrer.includes('android-app://');
    }

    /**
     * Initialize session persistence if in PWA context
     */
    init() {
        if (!this.isPWA) {
            console.log('SessionPersistence: Not in PWA context, skipping');
            return;
        }

        console.log('SessionPersistence: PWA detected, enabling session persistence');

        // Restore session on page load
        this.restoreSession();

        // Save session data when user logs in
        this.watchForLogin();

        // Clear stored data on logout
        this.watchForLogout();
    }

    /**
     * Store essential session data in localStorage for PWA
     */
    saveSessionData() {
        if (!this.isPWA) return;

        try {
            const sessionData = {
                timestamp: Date.now(),
                userLoggedIn: this.isUserLoggedIn(),
                currentUser: this.getCurrentUserFromDOM(),
                loginTimestamp: Date.now()
            };

            localStorage.setItem(this.sessionKey, JSON.stringify(sessionData));
            console.log('SessionPersistence: Session data saved', sessionData);
        } catch (error) {
            console.error('SessionPersistence: Error saving session data', error);
        }
    }

    /**
     * Restore session data from localStorage
     */
    restoreSession() {
        if (!this.isPWA) return;

        try {
            const stored = localStorage.getItem(this.sessionKey);
            if (!stored) {
                console.log('SessionPersistence: No stored session data');
                return;
            }

            const sessionData = JSON.parse(stored);
            const age = Date.now() - sessionData.timestamp;
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours

            if (age > maxAge) {
                console.log('SessionPersistence: Stored session too old, clearing');
                this.clearStoredSession();
                return;
            }

            // If user appears logged out but we have recent session data,
            // show a restore prompt or automatically attempt restoration
            if (sessionData.userLoggedIn && !this.isUserLoggedIn()) {
                this.promptSessionRestore(sessionData);
            }

        } catch (error) {
            console.error('SessionPersistence: Error restoring session', error);
            this.clearStoredSession();
        }
    }

    /**
     * Check if user appears to be logged in based on DOM elements
     */
    isUserLoggedIn() {
        // Look for indicators that user is logged in
        const logoutLink = document.querySelector('a[href*="/logout"]');
        const loginForm = document.querySelector('form[action*="/login"]');
        const currentUserElement = document.querySelector('[data-current-user]');

        return !loginForm && (logoutLink || currentUserElement);
    }

    /**
     * Extract current user info from DOM
     */
    getCurrentUserFromDOM() {
        const userElement = document.querySelector('[data-current-user]');
        return userElement ? userElement.textContent.trim() : null;
    }

    /**
     * Prompt user to restore their session
     */
    promptSessionRestore(sessionData) {
        // Prevent infinite loops - check if restoration already attempted
        if (this.restorationInProgress) {
            console.log('SessionPersistence: Restoration already in progress, skipping');
            return;
        }

        if (this.restorationAttempts >= this.maxRestorationAttempts) {
            console.log('SessionPersistence: Max restoration attempts reached, disabling auto-restore');
            this.clearStoredSession();
            return;
        }

        this.restorationInProgress = true;
        this.restorationAttempts++;

        // Set timeout to prevent hanging restoration attempts
        const timeoutId = setTimeout(() => {
            this.restorationInProgress = false;
            console.log('SessionPersistence: Restoration attempt timed out');
        }, this.restorationTimeout);

        const message = `You were previously logged in as ${sessionData.currentUser || 'a user'}. Would you like to restore your session?`;

        if (confirm(message)) {
            // Instead of redirecting to /, try to validate session first
            this.attemptSessionValidation(sessionData, timeoutId);
        } else {
            // User declined restoration
            clearTimeout(timeoutId);
            this.restorationInProgress = false;
            this.clearStoredSession();
        }
    }

    /**
     * Attempt to validate session with backend
     */
    async attemptSessionValidation(sessionData, timeoutId) {
        try {
            // Use the new session validation endpoint
            const response = await fetch('/validate-session', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                if (result.valid) {
                    // Session is valid, reload to show authenticated content
                    console.log('SessionPersistence: Session validation successful');
                    window.location.reload();
                } else {
                    // Session invalid, clear stored data
                    console.log(`SessionPersistence: Session validation failed - ${result.reason}`);
                    this.clearStoredSession();
                    window.location.href = '/login';
                }
            } else {
                // Validation endpoint not available or error, fall back to old method
                console.log('SessionPersistence: Validation endpoint failed, trying fallback method');
                await this.fallbackSessionValidation(sessionData);
            }
        } catch (error) {
            console.error('SessionPersistence: Session validation failed', error);
            // On error, try fallback method
            await this.fallbackSessionValidation(sessionData);
        } finally {
            clearTimeout(timeoutId);
            this.restorationInProgress = false;
        }
    }

    /**
     * Fallback session validation using homepage content parsing
     */
    async fallbackSessionValidation(sessionData) {
        try {
            const response = await fetch('/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            });

            if (response.ok) {
                const text = await response.text();
                // Check if response contains login form (indicating not logged in)
                if (text.includes('action="/login"') || text.includes('href="/login"')) {
                    // Not logged in, session invalid
                    console.log('SessionPersistence: Fallback validation - not logged in');
                    this.clearStoredSession();
                    window.location.href = '/login';
                } else {
                    // Appears logged in, reload page to show content
                    console.log('SessionPersistence: Fallback validation successful');
                    window.location.reload();
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('SessionPersistence: Fallback validation failed', error);
            // On complete failure, go to login
            this.clearStoredSession();
            window.location.href = '/login';
        }
    }

    /**
     * Watch for login events to save session data
     */
    watchForLogin() {
        // Monitor for successful login (page navigation away from login page)
        if (window.location.pathname === '/login') {
            // On login page, wait for form submission
            const loginForm = document.querySelector('form[action*="/login"]');
            if (loginForm) {
                loginForm.addEventListener('submit', () => {
                    // Delay to allow form processing
                    setTimeout(() => this.saveSessionData(), 1000);
                });
            }
        } else if (this.isUserLoggedIn()) {
            // On other pages, if user is logged in, save session data
            this.saveSessionData();
        }
    }

    /**
     * Watch for logout events to clear stored data
     */
    watchForLogout() {
        const logoutLink = document.querySelector('a[href*="/logout"]');
        if (logoutLink) {
            logoutLink.addEventListener('click', () => {
                this.clearStoredSession();
            });
        }
    }

    /**
     * Clear stored session data
     */
    clearStoredSession() {
        try {
            localStorage.removeItem(this.sessionKey);
            console.log('SessionPersistence: Stored session data cleared');
        } catch (error) {
            console.error('SessionPersistence: Error clearing session data', error);
        }
    }

    /**
     * Get debug info about session persistence state
     */
    getDebugInfo() {
        return {
            isPWA: this.isPWA,
            userLoggedIn: this.isUserLoggedIn(),
            storedSession: localStorage.getItem(this.sessionKey),
            currentUser: this.getCurrentUserFromDOM(),
            restorationAttempts: this.restorationAttempts,
            restorationInProgress: this.restorationInProgress,
            maxRestorationAttempts: this.maxRestorationAttempts
        };
    }

    /**
     * Reset restoration attempts (for debugging/testing)
     */
    resetRestorationAttempts() {
        this.restorationAttempts = 0;
        this.restorationInProgress = false;
        console.log('SessionPersistence: Restoration attempts reset');
    }
}

// Initialize session persistence when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sessionPersistence = new SessionPersistence();
});

// Export for debugging
window.SessionPersistence = SessionPersistence;
