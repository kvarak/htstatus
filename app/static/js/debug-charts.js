/**
 * Simple Chart State Management
 * Applies simplification hierarchy: reduce complexity, eliminate duplication
 */

// Simple chart state transitions using data attributes and CSS classes
document.addEventListener('DOMContentLoaded', async function() {
    const container = document.getElementById('chartsContainer');
    if (!container) return;

    // Load saved preferences first
    await loadPreferences();

    // Single event listener with delegation - much simpler than complex class setup
    container.addEventListener('click', function(e) {
        const shrinkBtn = e.target.closest('.chart-shrink');
        const expandBtn = e.target.closest('.chart-expand');

        if (!shrinkBtn && !expandBtn) return;

        const chartContainer = e.target.closest('[data-chart-id]');
        const card = chartContainer.querySelector('.chart-card');
        if (!card) return;

        // Get current mode from data attribute (single source of truth)
        let currentMode = card.dataset.mode || 'normal';
        let newMode;

        if (shrinkBtn && currentMode !== 'minimized') {
            // normal -> minimized, full -> normal
            newMode = currentMode === 'normal' ? 'minimized' : 'normal';
        } else if (expandBtn && currentMode !== 'full') {
            // normal -> full, minimized -> normal
            newMode = currentMode === 'normal' ? 'full' : 'normal';
        }

        if (newMode) {
            setChartMode(chartContainer, newMode);
            savePreferences(); // Save state changes
        }
    });

    // Initialize all charts to proper state
    container.querySelectorAll('[data-chart-id]').forEach(chart => {
        const mode = chart.querySelector('.chart-card').dataset.mode || 'normal';
        setChartMode(chart, mode);
        setupDragAndDrop(chart);
    });
});

// Simple state setter - no complex preferences, just CSS classes
function setChartMode(chartContainer, mode) {
    const card = chartContainer.querySelector('.chart-card');
    if (!card) return;

    // Update data attribute (single source of truth)
    card.dataset.mode = mode;

    // Update CSS classes for width control
    chartContainer.classList.remove('chart-minimized', 'chart-normal', 'chart-full-width');
    chartContainer.classList.add(`chart-${mode === 'full' ? 'full-width' : mode}`);

    // Update button states
    updateButtons(chartContainer, mode);

    // Resize chart if it exists
    const chartId = chartContainer.dataset.chartId;
    if (window.chartInstances && window.chartInstances[chartId]) {
        setTimeout(() => window.chartInstances[chartId].resize(), 100);
    }
}

// Simple button state management
function updateButtons(chartContainer, mode) {
    const shrinkBtn = chartContainer.querySelector('.chart-shrink');
    const expandBtn = chartContainer.querySelector('.chart-expand');

    // Reset both buttons
    [shrinkBtn, expandBtn].forEach(btn => {
        if (btn) {
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
            btn.classList.remove('disabled');
        }
    });

    // Disable appropriate button for each state
    if (mode === 'minimized' && shrinkBtn) {
        shrinkBtn.style.opacity = '0.5';
        shrinkBtn.style.pointerEvents = 'none';
    } else if (mode === 'full' && expandBtn) {
        expandBtn.style.opacity = '0.5';
        expandBtn.style.pointerEvents = 'none';
    }
}

// Simple drag and drop - minimal implementation
function setupDragAndDrop(chartContainer) {
    const dragHandle = chartContainer.querySelector('.chart-drag-handle');
    if (!dragHandle) return;

    chartContainer.draggable = true;

    chartContainer.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', chartContainer.dataset.chartId);
        chartContainer.style.opacity = '0.5';
    });

    chartContainer.addEventListener('dragend', (e) => {
        chartContainer.style.opacity = '1';
        document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
    });

    chartContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (!chartContainer.classList.contains('drag-over')) {
            chartContainer.classList.add('drag-over');
        }
    });

    chartContainer.addEventListener('dragleave', (e) => {
        // Only remove if we're truly leaving the element
        const rect = chartContainer.getBoundingClientRect();
        if (e.clientX < rect.left || e.clientX > rect.right ||
            e.clientY < rect.top || e.clientY > rect.bottom) {
            chartContainer.classList.remove('drag-over');
        }
    });

    chartContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        const draggedId = e.dataTransfer.getData('text/plain');
        const draggedElement = document.querySelector(`[data-chart-id="${draggedId}"]`);
        const dropTarget = chartContainer;

        if (draggedElement && dropTarget && draggedId !== dropTarget.dataset.chartId) {
            // Simple reorder: insert dragged element before drop target
            dropTarget.parentNode.insertBefore(draggedElement, dropTarget);
            savePreferences(); // Save order changes
        }

        dropTarget.classList.remove('drag-over');
    });
}

// Simple database persistence - minimal implementation
async function loadPreferences() {
    try {
        const response = await fetch('/api/admin/preferences');
        if (!response.ok) return;

        const data = await response.json();
        if (!data.chart_layout) return;

        const container = document.getElementById('chartsContainer');
        if (!container) return;

        // Apply saved modes
        if (data.chart_layout.chart_modes) {
            Object.entries(data.chart_layout.chart_modes).forEach(([chartId, mode]) => {
                const chart = container.querySelector(`[data-chart-id="${chartId}"]`);
                if (chart) {
                    chart.querySelector('.chart-card').dataset.mode = mode;
                }
            });
        }

        // Apply saved order
        if (data.chart_layout.chart_order) {
            data.chart_layout.chart_order.forEach(chartId => {
                const chart = container.querySelector(`[data-chart-id="${chartId}"]`);
                if (chart) container.appendChild(chart);
            });
        }
    } catch (e) {
        console.warn('Could not load preferences:', e);
    }
}

async function savePreferences() {
    try {
        const container = document.getElementById('chartsContainer');
        if (!container) return;

        const charts = container.querySelectorAll('[data-chart-id]');
        const chartOrder = Array.from(charts).map(chart => chart.dataset.chartId);
        const chartModes = {};

        charts.forEach(chart => {
            const mode = chart.querySelector('.chart-card').dataset.mode || 'normal';
            chartModes[chart.dataset.chartId] = mode;
        });

        const preferences = {
            chart_layout: {
                chart_order: chartOrder,
                chart_modes: chartModes
            }
        };

        await fetch('/api/admin/preferences', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(preferences)
        });
    } catch (e) {
        console.warn('Could not save preferences:', e);
    }
}