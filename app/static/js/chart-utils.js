/**
 * Chart.js v4.x Utilities for HattrickPlanner
 * Centralized chart configuration and common patterns
 */

class HattrickCharts {
    constructor() {
        this.defaultColors = {
            primary: 'hsl(120, 45%, 25%)',      // Football green
            success: 'hsl(120, 70%, 35%)',      // Success green
            warning: 'hsl(45, 90%, 55%)',       // Warning yellow
            danger: 'hsl(0, 84%, 60%)',         // Danger red
            secondary: 'hsl(0, 0%, 75%)',       // Gray
            background: 'hsl(120, 8%, 97%)'     // Light background
        };

        this.skillColors = [
            'hsl(120, 45%, 25%)',   // Keeper - primary green
            'hsl(140, 50%, 30%)',   // Defender - darker green
            'hsl(100, 60%, 35%)',   // Playmaker - lighter green
            'hsl(80, 55%, 40%)',    // Winger - yellow-green
            'hsl(60, 70%, 45%)',    // Passing - yellow
            'hsl(40, 80%, 50%)',    // Scorer - orange
            'hsl(20, 85%, 55%)'     // Set pieces - red-orange
        ];
    }

    /**
     * Create default chart configuration with responsive design
     */
    getDefaultConfig(type = 'line') {
        return {
            type: type,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                scales: type !== 'doughnut' && type !== 'pie' ? {
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        beginAtZero: true
                    }
                } : undefined
            }
        };
    }

    /**
     * Create player skill progression chart
     */
    createSkillChart(canvasId, playerData, skillName) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = this.getDefaultConfig('line');

        // Customize for skill progression
        config.data = {
            labels: playerData.weeks,
            datasets: [{
                label: skillName,
                data: playerData.values,
                borderColor: this.defaultColors.primary,
                backgroundColor: this.defaultColors.primary + '20',
                tension: 0.3,
                fill: true
            }]
        };

        config.options.scales.y.min = Math.max(0, Math.min(...playerData.values) - 1);
        config.options.scales.y.max = Math.max(...playerData.values) + 1;
        config.options.scales.y.ticks = {
            stepSize: 1
        };

        return new Chart(ctx, config);
    }

    /**
     * Create multi-skill comparison chart
     */
    createMultiSkillChart(canvasId, playerData, skills) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = this.getDefaultConfig('line');

        config.data = {
            labels: playerData.weeks,
            datasets: skills.map((skill, index) => ({
                label: skill.name,
                data: skill.values,
                borderColor: this.skillColors[index % this.skillColors.length],
                backgroundColor: this.skillColors[index % this.skillColors.length] + '20',
                tension: 0.3
            }))
        };

        return new Chart(ctx, config);
    }

    /**
     * Create activity/usage statistics chart
     */
    createStatsChart(canvasId, data, chartType = 'bar') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        const config = this.getDefaultConfig(chartType);

        config.data = {
            labels: data.labels,
            datasets: [{
                label: data.title || 'Statistics',
                data: data.values,
                backgroundColor: chartType === 'doughnut' || chartType === 'pie'
                    ? this.skillColors
                    : this.defaultColors.primary,
                borderColor: this.defaultColors.primary,
                borderWidth: 1
            }]
        };

        // Special configuration for pie/doughnut charts
        if (chartType === 'doughnut' || chartType === 'pie') {
            config.options.plugins.legend.position = 'right';
        }

        return new Chart(ctx, config);
    }

    /**
     * Destroy chart safely
     */
    destroyChart(chartInstance) {
        if (chartInstance && typeof chartInstance.destroy === 'function') {
            chartInstance.destroy();
        }
    }

    /**
     * Update chart data
     */
    updateChart(chartInstance, newData) {
        if (!chartInstance || !newData) return;

        chartInstance.data = newData;
        chartInstance.update();
    }

    /**
     * Resize chart for mobile responsiveness
     */
    handleResize(chartInstance) {
        if (chartInstance && typeof chartInstance.resize === 'function') {
            chartInstance.resize();
        }
    }
}

// Global instance for use across templates
window.hattrickCharts = new HattrickCharts();

// Global utility functions for backward compatibility
window.createPlayerChart = function(canvasId, playerData, skillName) {
    return window.hattrickCharts.createSkillChart(canvasId, playerData, skillName);
};

window.createStatsChart = function(canvasId, data, type) {
    return window.hattrickCharts.createStatsChart(canvasId, data, type);
};