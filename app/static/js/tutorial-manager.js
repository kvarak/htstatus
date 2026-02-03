/**
 * Tutorial Manager for HattrickPlanner
 * Manages guided tours and feature discovery using Intro.js
 */

class TutorialManager {
    constructor() {
        this.storageKey = 'ht_tutorial_progress';
        this.sessionId = this.generateSessionId();
        this.tourStartTime = null;
        this.stepStartTime = null;
        this.tourCompleted = false; // Track if tour completed to avoid double events
        console.log('TutorialManager loaded [FIXED VERSION - ' + new Date().toISOString() + ']');
        this.init();
    }

    /**
     * Generate a session ID for analytics tracking
     */
    generateSessionId() {
        // Create a simple session ID based on timestamp and random value
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Send analytics event to server
     */
    async sendAnalyticsEvent(eventType, tourId, stepNumber = null, stepDuration = null, totalDuration = null) {
        try {
            const analyticsData = {
                session_id: this.sessionId,
                event_type: eventType,
                tour_id: tourId,
                page_path: window.location.pathname,
                step_number: stepNumber,
                step_duration_seconds: stepDuration,
                total_duration_seconds: totalDuration
            };

            const response = await fetch('/api/tutorial-analytics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(analyticsData)
            });

            if (!response.ok) {
                console.warn('Failed to send analytics:', response.statusText);
            } else {
                console.log(`📊 Analytics: ${eventType} for ${tourId}`);
            }
        } catch (error) {
            console.warn('Error sending tutorial analytics:', error);
        }
    }

    /**
     * Initialize tutorial system
     */
    init() {
        // Check if intro.js is loaded
        if (typeof window.introJs !== 'function') {
            console.warn('Intro.js not loaded yet, retrying in 100ms...');
            setTimeout(() => this.init(), 100);
            return;
        }

        this.progress = this.loadProgress();
        this.setupTours();
        this.checkForNewFeatureAlerts();

        // Check for context-specific tours (no auto-start)
        this.checkForContextualTours();
    }

    /**
     * Load tutorial progress from localStorage
     */
    loadProgress() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : {
                welcomeCompleted: false,
                toursCompleted: {},
                featuresViewed: {},
                lastVersion: null,
                tourPromptsDisabled: {}
            };
        } catch (e) {
            console.warn('Failed to load tutorial progress:', e);
            return {
                welcomeCompleted: false,
                toursCompleted: {},
                featuresViewed: {},
                lastVersion: null,
                tourPromptsDisabled: {}
            };
        }
    }

    /**
     * Save tutorial progress to localStorage
     */
    saveProgress() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.progress));
        } catch (e) {
            console.warn('Failed to save tutorial progress:', e);
        }
    }

    /**
     * Show tour prompt with "Don't ask again" option
     */
    showTourPrompt(message, tourId) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 10000; display: flex;
            align-items: center; justify-content: center;
        `;

        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: white; padding: 20px; border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3); max-width: 400px;
            text-align: center; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
        `;

        dialog.innerHTML = `
            <p style="margin-bottom: 20px; font-size: 16px;">${message}</p>
            <div style="margin-bottom: 20px;">
                <label style="display: flex; align-items: center; justify-content: center; cursor: pointer;">
                    <input type="checkbox" id="dontAskAgain" style="margin-right: 8px;">
                    Don't ask again
                </label>
            </div>
            <div>
                <button id="startTour" style="margin-right: 10px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Yes, show me
                </button>
                <button id="skipTour" style="padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    No thanks
                </button>
            </div>
        `;

        modal.appendChild(dialog);
        document.body.appendChild(modal);

        return new Promise((resolve) => {
            const cleanup = () => {
                document.body.removeChild(modal);
            };

            const handleChoice = (startTour) => {
                const dontAskAgain = dialog.querySelector('#dontAskAgain').checked;

                if (dontAskAgain) {
                    if (!this.progress.tourPromptsDisabled) {
                        this.progress.tourPromptsDisabled = {};
                    }
                    this.progress.tourPromptsDisabled[tourId] = true;
                    this.saveProgress();
                }

                cleanup();
                resolve(startTour);
            };

            dialog.querySelector('#startTour').onclick = () => handleChoice(true);
            dialog.querySelector('#skipTour').onclick = () => handleChoice(false);
            modal.onclick = (e) => {
                if (e.target === modal) handleChoice(false);
            };
        });
    }

    /**
     * Check if user should see the welcome tour
     */
    shouldShowWelcomeTour() {
        // Show welcome tour if:
        // 1. Never completed before
        // 2. User is authenticated (has session data)
        // 3. We're on the main page
        return !this.progress.welcomeCompleted &&
               window.location.pathname === '/' &&
               this.isUserAuthenticated();
    }

    /**
     * Check if user is authenticated (simplified check)
     */
    isUserAuthenticated() {
        // Look for authenticated page elements - more reliable indicators
        return document.querySelector('[data-current-user]') !== null ||
               document.getElementById('navbar-update-link') !== null ||
               document.getElementById('navbar-settings-link') !== null ||
               document.querySelector('#navbar-authenticated .nav-link[href="/logout"]') !== null;
    }

    /**
     * Start the welcome tour for new users
     */
    startWelcomeTour() {
        if (typeof window.introJs !== 'function') {
            console.warn('Intro.js not available for startWelcomeTour');
            return;
        }

        const tour = introJs();

        tour.setOptions({
            steps: [
                {
                    intro: "Welcome to HattrickPlanner! 👋<br>Let's take a quick tour to help you get started with managing your Hattrick team data."
                },
                {
                    element: '#navbar-team-dropdown',
                    intro: "Visit your <strong>Team</strong> dropdown to access various team management tools including Players, Training, and Statistics.",
                    position: 'bottom'
                },
                {
                    element: '#navbar-players-link',
                    intro: "The <strong>Players</strong> page shows detailed player information, skills, and training progress. This is where you'll spend most of your time analyzing your squad.",
                    position: 'bottom'
                },
                {
                    element: '#navbar-training-link',
                    intro: "Track your team's <strong>Training</strong> data and see how your players are developing over time.",
                    position: 'bottom'
                },
                {
                    element: '#navbar-stats-link',
                    intro: "Review team <strong>Statistics</strong> and get insights into your squad's overall performance.",
                    position: 'bottom'
                },
                {
                    element: '#navbar-update-link',
                    intro: "Use <strong>Update</strong> to sync your latest data from Hattrick. This fetches fresh player stats and match data. You should do this regularly!",
                    position: 'bottom'
                },
                {
                    element: '#navbar-settings-link',
                    intro: "In <strong>Settings</strong>, customize your display preferences and manage your account.",
                    position: 'bottom'
                },
                {
                    intro: "That's the basics! 🎉<br>Explore each section to discover detailed statistics and analysis tools for your Hattrick team.<br><br>You can reset the tour in the Settings."
                }
            ],
            showProgress: true,
            showBullets: false,
            exitOnOverlayClick: false,
            exitOnEsc: true,
            nextLabel: 'Next →',
            prevLabel: '← Back',
            doneLabel: 'Get Started!',
            skipLabel: 'Skip Tour',
            buttonClass: 'btn btn-sm',
            highlightClass: 'introjs-custom-highlight',
            tooltipClass: 'introjs-custom-tooltip'
        });

        tour.onexit(() => {
            // Only track skip if tour wasn't completed
            if (!this.tourCompleted) {
                const totalDuration = this.tourStartTime ? (Date.now() - this.tourStartTime) / 1000 : null;
                this.sendAnalyticsEvent('skip', 'welcome', tour._currentStep, null, totalDuration);
            }
            this.markWelcomeTourCompleted();
        });

        tour.oncomplete(() => {
            // Mark as completed to prevent skip tracking
            this.tourCompleted = true;
            const totalDuration = this.tourStartTime ? (Date.now() - this.tourStartTime) / 1000 : null;
            this.sendAnalyticsEvent('complete', 'welcome', null, null, totalDuration);
            this.markWelcomeTourCompleted();
        });

        // Auto-advance when team dropdown is clicked during step 2 (index 1)
        tour.onbeforechange((targetElement) => {
            const currentStep = tour._currentStep;

            // Track step duration if we have a previous step
            if (this.stepStartTime && currentStep > 0) {
                const stepDuration = (Date.now() - this.stepStartTime) / 1000;
                this.sendAnalyticsEvent('step', 'welcome', currentStep - 1, stepDuration);
            }

            // Start timing the new step
            this.stepStartTime = Date.now();

            // Step 2 is the team dropdown step (index 1)
            if (currentStep === 1) {
                // Grey out the Next button to encourage user interaction
                setTimeout(() => {
                    const nextButton = document.querySelector('.introjs-nextbutton');
                    if (nextButton) {
                        nextButton.style.opacity = '0.5';
                        nextButton.style.cursor = 'not-allowed';
                        nextButton.disabled = true;
                        nextButton.title = 'Click the Team dropdown above to continue';
                    }
                }, 100);

                // Add click listener to team dropdown
                const teamDropdown = document.getElementById('navbar-team-dropdown');
                if (teamDropdown) {
                    const autoAdvance = () => {
                        // Re-enable the Next button
                        const nextButton = document.querySelector('.introjs-nextbutton');
                        if (nextButton) {
                            nextButton.style.opacity = '';
                            nextButton.style.cursor = '';
                            nextButton.disabled = false;
                            nextButton.title = '';
                        }

                        // Remove the event listener to prevent multiple triggers
                        teamDropdown.removeEventListener('click', autoAdvance);
                        // Auto-advance to next step after a short delay
                        setTimeout(() => {
                            tour.nextStep();
                        }, 500);
                    };
                    teamDropdown.addEventListener('click', autoAdvance);
                }
            }
            // Keep dropdown open for steps 2-5 (team dropdown items: Players, Training, Stats, Update)
            else if (currentStep >= 2 && currentStep <= 5) {
                // Force dropdown to stay open
                setTimeout(() => {
                    const teamDropdown = document.getElementById('navbar-team-dropdown');
                    if (teamDropdown) {
                        // Check if dropdown menu is visible by looking for Bootstrap's 'show' class
                        const dropdownMenu = teamDropdown.nextElementSibling;
                        if (dropdownMenu && !dropdownMenu.classList.contains('show')) {
                            // Force dropdown open by triggering click
                            teamDropdown.click();
                        }
                    }
                }, 100);

                // Ensure Next button is enabled for dropdown item steps
                setTimeout(() => {
                    const nextButton = document.querySelector('.introjs-nextbutton');
                    if (nextButton) {
                        nextButton.style.opacity = '';
                        nextButton.style.cursor = '';
                        nextButton.disabled = false;
                        nextButton.title = '';
                    }
                }, 100);
            }
            else {
                // Ensure Next button is enabled for other steps
                setTimeout(() => {
                    const nextButton = document.querySelector('.introjs-nextbutton');
                    if (nextButton) {
                        nextButton.style.opacity = '';
                        nextButton.style.cursor = '';
                        nextButton.disabled = false;
                        nextButton.title = '';
                    }
                }, 100);
            }
        });

        // Ensure dropdown stays open after step transitions for dropdown-related steps
        tour.onafterchange((targetElement) => {
            const currentStep = tour._currentStep;

            // Keep dropdown open for steps 2-5 (Players, Training, Stats, Update)
            if (currentStep >= 2 && currentStep <= 5) {
                setTimeout(() => {
                    const teamDropdown = document.getElementById('navbar-team-dropdown');
                    if (teamDropdown) {
                        const dropdownMenu = teamDropdown.nextElementSibling;
                        if (dropdownMenu && !dropdownMenu.classList.contains('show')) {
                            teamDropdown.click();
                        }
                    }
                }, 200); // Slightly longer delay to ensure intro.js has finished transitioning
            }
        });

        // Track tour start and initialize timing
        this.tourStartTime = Date.now();
        this.stepStartTime = Date.now();
        this.tourCompleted = false; // Reset completion flag
        this.sendAnalyticsEvent('start', 'welcome');

        tour.start();
    }

    /**
     * Mark welcome tour as completed
     */
    markWelcomeTourCompleted() {
        this.progress.welcomeCompleted = true;
        this.saveProgress();

        // Remove help button since welcome tour is now completed
        this.removeHelpButtonIfNoTours();
    }

    /**
     * Start a specific feature tour
     */
    startFeatureTour(featureName) {
        if (typeof window.introJs !== 'function') {
            console.warn('Intro.js not available for startFeatureTour');
            return;
        }

        const tourConfig = this.getFeatureTourConfig(featureName);
        if (!tourConfig) {
            console.warn(`No tour configuration found for feature: ${featureName}`);
            return;
        }

        const tour = introJs();
        tour.setOptions(tourConfig.options);

        // Track tour events
        tour.onexit(() => {
            // Only track skip if tour wasn't completed
            if (!this.tourCompleted) {
                const totalDuration = this.tourStartTime ? (Date.now() - this.tourStartTime) / 1000 : null;
                this.sendAnalyticsEvent('skip', featureName, tour._currentStep, null, totalDuration);
            }
            this.markFeatureTourCompleted(featureName);
        });

        tour.oncomplete(() => {
            // Mark as completed to prevent skip tracking
            this.tourCompleted = true;
            const totalDuration = this.tourStartTime ? (Date.now() - this.tourStartTime) / 1000 : null;
            this.sendAnalyticsEvent('complete', featureName, null, null, totalDuration);
            this.markFeatureTourCompleted(featureName);
        });

        // Track step changes
        tour.onbeforechange((targetElement) => {
            const currentStep = tour._currentStep;

            // Track step duration if we have a previous step
            if (this.stepStartTime && currentStep > 0) {
                const stepDuration = (Date.now() - this.stepStartTime) / 1000;
                this.sendAnalyticsEvent('step', featureName, currentStep - 1, stepDuration);
            }

            // Start timing the new step
            this.stepStartTime = Date.now();
        });

        // Track tour start and initialize timing
        this.tourStartTime = Date.now();
        this.stepStartTime = Date.now();
        this.tourCompleted = false; // Reset completion flag
        this.sendAnalyticsEvent('start', featureName);

        tour.start();
    }

    /**
     * Get tour configuration for specific features
     */
    getFeatureTourConfig(featureName) {
        const configs = {
            'player-management': {
                options: {
                    steps: [
                        {
                            intro: "Let's explore <strong>Player Management</strong> features! This page helps you analyze your squad in detail."
                        },
                        {
                            element: '#player-table',
                            intro: "This table shows all your players with their current skills and statistics. Each row represents one player.",
                            position: 'top'
                        },
                        {
                            element: '.table-custom thead',
                            intro: "Each column represents a different skill or attribute. Use these values to identify player strengths and weaknesses.",
                            position: 'bottom'
                        },
                        {
                            element: '.sortable',
                            intro: "Click any column header to sort players by that skill. This is great for finding your best defenders, playmakers, or scorers!",
                            position: 'top'
                        },
                        {
                            element: '.table-custom tbody tr:first-child',
                            intro: "💡 <strong>Pro tip:</strong> Click on any player name to see detailed skill progression charts and training history. This helps you track development over time!",
                            position: 'bottom'
                        },
                        {
                            intro: "Player groups help organize your squad by position, training focus, or any custom categories you choose. You can assign players to groups from their individual player details page."
                        }
                    ],
                    showProgress: true,
                    nextLabel: 'Next →',
                    prevLabel: '← Back',
                    doneLabel: 'Got it!',
                    buttonClass: 'btn btn-sm',
                    highlightClass: 'introjs-custom-highlight',
                    tooltipClass: 'introjs-custom-tooltip'
                }
            },
            'data-update': {
                options: {
                    steps: [
                        {
                            intro: "Let's learn about <strong>Data Updates</strong>! Keeping your data fresh is crucial for accurate analysis."
                        },
                        {
                            intro: "Click 'Update data' regularly to fetch the latest player skills, match results, and team information from Hattrick."
                        },
                        {
                            intro: "💡 <strong>Tip:</strong> Update after matches, training sessions, or player transfers to keep your analysis current!"
                        }
                    ],
                    showProgress: true,
                    nextLabel: 'Next →',
                    prevLabel: '← Back',
                    doneLabel: 'Got it!',
                    buttonClass: 'btn btn-sm',
                    highlightClass: 'introjs-custom-highlight',
                    tooltipClass: 'introjs-custom-tooltip'
                }
            }
        };

        return configs[featureName] || null;
    }

    /**
     * Mark feature tour as completed
     */
    markFeatureTourCompleted(featureName) {
        this.progress.toursCompleted[featureName] = true;
        this.saveProgress();

        // Remove help button if no more tours are available for this page
        this.removeHelpButtonIfNoTours();
    }

    /**
     * Check for new features and show alerts
     */
    checkForNewFeatureAlerts() {
        // Get current app version (could be from meta tag or global variable)
        const currentVersion = this.getCurrentAppVersion();

        if (this.progress.lastVersion && this.progress.lastVersion !== currentVersion) {
            this.showNewFeatureAlerts(this.progress.lastVersion, currentVersion);
        }

        this.progress.lastVersion = currentVersion;
        this.saveProgress();
    }

    /**
     * Get current app version
     */
    getCurrentAppVersion() {
        // Try to get version from meta tag or global variable
        const metaVersion = document.querySelector('meta[name="app-version"]');
        return metaVersion ? metaVersion.content : '1.0.0';
    }

    /**
     * Show new feature alerts
     */
    showNewFeatureAlerts(oldVersion, newVersion) {
        // This could be expanded to show specific feature notifications
        // For now, just show a generic update message
        console.log(`App updated from ${oldVersion} to ${newVersion}`);
    }

    /**
     * Setup tour configurations - no longer automatically adds help button
     */
    setupTours() {
        // Tour configurations are now handled dynamically
        // Help button is added only when tours are available
    }

    /**
     * Add help button for available tour
     */
    addHelpButton(tour) {
        const helpBtn = document.createElement('button');
        helpBtn.id = 'tutorial-help-btn';
        helpBtn.innerHTML = '?';
        helpBtn.title = `Click for ${tour.name}`;
        helpBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1050;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            background-color: #007bff;
            color: white;
            border: none;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        `;

        // Add hover effect
        helpBtn.onmouseenter = () => {
            helpBtn.style.backgroundColor = '#0056b3';
        };
        helpBtn.onmouseleave = () => {
            helpBtn.style.backgroundColor = '#007bff';
        };

        // Add click handler to directly start the tour
        helpBtn.addEventListener('click', () => {
            this.startTourForCurrentPage(tour);
        });

        document.body.appendChild(helpBtn);
    }

    /**
     * Start the appropriate tour for the current page
     */
    startTourForCurrentPage(tour) {
        // Track help button click
        this.sendAnalyticsEvent('help_click', tour.id);

        switch (tour.id) {
            case 'welcome':
                this.startWelcomeTour();
                break;
            case 'player-management':
            case 'data-update':
                this.startFeatureTour(tour.id);
                break;
            default:
                console.warn(`Unknown tour: ${tour.id}`);
        }
    }

    /**
     * Show help menu with tutorial options
     */
    showHelpMenu() {
        const options = [
            'Restart Welcome Tour',
            'Player Management Help',
            'Data Update Help',
            'Reset All Tutorial Progress',
            'Cancel'
        ];

        const choice = prompt(`Choose an option:\n\n${options.map((opt, i) => `${i + 1}. ${opt}`).join('\n')}`);
        const choiceNum = parseInt(choice);

        switch (choiceNum) {
            case 1:
                this.restartWelcomeTour();
                break;
            case 2:
                this.startFeatureTour('player-management');
                break;
            case 3:
                this.startFeatureTour('data-update');
                break;
            case 4:
                if (confirm('Reset all tutorial progress? This will make help buttons (?) appear again on pages with available tutorials.')) {
                    this.resetAllProgress();
                }
                break;
            default:
                break;
        }
    }

    /**
     * Restart welcome tour (reset progress)
     */
    restartWelcomeTour() {
        this.progress.welcomeCompleted = false;
        this.saveProgress();
        setTimeout(() => this.startWelcomeTour(), 100);
    }

    /**
     * Check for context-specific tours based on current page
     */
    checkForContextualTours() {
        // Debug log to help troubleshoot
        const currentPath = window.location.pathname;
        const isAuth = this.isUserAuthenticated();
        const welcomeCompleted = this.progress.welcomeCompleted;
        console.log('Tutorial debug - Path:', currentPath, 'Auth:', isAuth, 'Welcome completed:', welcomeCompleted);

        // Only add help button if there's an available tour for this page
        // No automatic prompts or tour starts
        this.addHelpButtonIfTourAvailable();
    }

    /**
     * Get the tour available for the current page
     */
    getCurrentPageTour() {
        const currentPath = window.location.pathname;

        // Welcome tour for main page (must be authenticated)
        if (currentPath === '/' && !this.progress.welcomeCompleted && this.isUserAuthenticated()) {
            return { id: 'welcome', name: 'Welcome Tour' };
        }

        // Player management tour
        if (currentPath.includes('/player') && !this.progress.toursCompleted['player-management']) {
            return { id: 'player-management', name: 'Player Management Help' };
        }

        // Data update tour (only for actual update pages, not just when link exists)
        if (currentPath.includes('/update') && !this.progress.toursCompleted['data-update']) {
            return { id: 'data-update', name: 'Data Update Help' };
        }

        return null;
    }

    /**
     * Check if help button should be shown and add it
     */
    addHelpButtonIfTourAvailable() {
        // Remove existing help button if any
        const existingBtn = document.getElementById('tutorial-help-btn');
        if (existingBtn) {
            existingBtn.remove();
        }

        const availableTour = this.getCurrentPageTour();
        if (!availableTour) {
            return; // No tour available for this page
        }

        // Create and add help button
        this.addHelpButton(availableTour);
    }

    /**
     * Remove help button if no tours are available for current page
     */
    removeHelpButtonIfNoTours() {
        const availableTour = this.getCurrentPageTour();
        if (!availableTour) {
            const existingBtn = document.getElementById('tutorial-help-btn');
            if (existingBtn) {
                existingBtn.remove();
            }
        }
    }

    /**
     * Reset all tutorial progress
     */
    resetAllProgress() {
        // Track reset event
        this.sendAnalyticsEvent('reset', 'all');

        // Reset everything including welcome tour
        localStorage.removeItem(this.storageKey);
        this.progress = this.loadProgress();
        this.saveProgress();
        console.log('Tutorial progress reset [' + new Date().toISOString() + ']');

        // Re-check for contextual tours after reset
        setTimeout(() => {
            this.checkForContextualTours();
        }, 1000);
    }
}

// Initialize tutorial manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.tutorialManager = new TutorialManager();
});

// Export for manual access
window.TutorialManager = TutorialManager;