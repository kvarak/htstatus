/**
 * PWA Session Persistence Manager
 * Handles session storage for Progressive Web App to prevent re-login requirements
 */

class SessionPersistence {
    constructor() {
        this.isPWA = this.detectPWA();
        this.sessionKey = 'ht_session_data';
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
        const message = `You were previously logged in as ${sessionData.currentUser || 'a user'}. Would you like to restore your session?`;

        if (confirm(message)) {
            // Redirect to a session restore endpoint or reload to trigger server-side session check
            window.location.href = '/';
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
            currentUser: this.getCurrentUserFromDOM()
        };
    }
}

// Initialize session persistence when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sessionPersistence = new SessionPersistence();
});

// Export for debugging
window.SessionPersistence = SessionPersistence;