/**
 * Chart.js v4.x Utilities for HattrickPlanner
 * Centralized chart configuration and common patterns
 */

// One restrained palette for every chart: green and slate (the two accents)
// in light/dark shades, plus one gray. Red only for "bad" values (errors, losses).
const CHART_PALETTE = [
    [125, 35, 30],
    [215, 28, 45],
    [125, 25, 55],
    [215, 25, 68],
    [0, 0, 55],
    [125, 20, 75],
    [215, 30, 28],
];
const CHART_DANGER = 'hsl(0, 65%, 50%)';

function chartColor(index, alpha = 1) {
    const [h, s, l] = CHART_PALETTE[index % CHART_PALETTE.length];
    return `hsla(${h}, ${s}%, ${l}%, ${alpha})`;
}

class HattrickCharts {
    constructor() {
        this.defaultColors = {
            primary: chartColor(0),
            success: chartColor(0),
            warning: 'hsl(40, 90%, 50%)',
            danger: CHART_DANGER,
            secondary: chartColor(3),
            background: 'hsl(0, 0%, 98%)'
        };

        this.skillColors = CHART_PALETTE.map((_, i) => chartColor(i));
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
                // Grid/tick colours come from Chart.defaults (set by dark-mode.js)
                scales: type !== 'doughnut' && type !== 'pie' ? {
                    x: {},
                    y: {
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
                backgroundColor: chartColor(0, 0.12),
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
                backgroundColor: chartColor(index, 0.12),
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

window.chartColor = chartColor;
window.CHART_DANGER = CHART_DANGER;

// Global utility functions for backward compatibility
window.createPlayerChart = function(canvasId, playerData, skillName) {
    return window.hattrickCharts.createSkillChart(canvasId, playerData, skillName);
};

window.createStatsChart = function(canvasId, data, type) {
    return window.hattrickCharts.createStatsChart(canvasId, data, type);
};
