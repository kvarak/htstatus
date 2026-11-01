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

/**
 * Line chart of several skills over time (training page).
 * skills: [{ name, values }], playerData.weeks: x-axis labels.
 */
function createMultiSkillChart(canvasId, playerData, skills) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: playerData.weeks,
            datasets: skills.map((skill, index) => ({
                label: skill.name,
                data: skill.values,
                borderColor: chartColor(index),
                backgroundColor: chartColor(index, 0.12),
                tension: 0.3
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { usePointStyle: true, padding: 15, font: { size: 12 } }
                }
            },
            // Grid/tick colours come from Chart.defaults (set by dark-mode.js)
            scales: { x: {}, y: { beginAtZero: true } }
        }
    });
}

window.chartColor = chartColor;
window.CHART_DANGER = CHART_DANGER;
window.createMultiSkillChart = createMultiSkillChart;
