/**
 * Enhanced Player Table with Filtering, Multi-Select, and Bulk Actions
 * Consolidates FEAT-026 (Batch Group Management) + FEAT-028 (Filtering) + FEAT-010 (Comparison)
 */

class PlayerTableEnhanced {
    constructor() {
        this.selectedPlayers = new Set();
        this.filteredPlayers = new Set();
        this.allPlayers = [];
        this.filterTimeout = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.collectPlayerData();
        this.restoreFiltersFromStorage();
        this.updateBulkActions();
    }

    setupEventListeners() {
        // Filter inputs
        const nameFilter = document.getElementById('name-filter');
        const groupCheckboxes = document.querySelectorAll('.group-checkbox');

        if (nameFilter) {
            nameFilter.addEventListener('input', this.debounce(() => this.applyFilters(), 300));
        }

        // Add event listeners for group checkboxes
        groupCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.value === '') {
                    // "All Groups" checkbox logic
                    if (e.target.checked) {
                        // Uncheck all other group checkboxes
                        groupCheckboxes.forEach(cb => {
                            if (cb.value !== '') cb.checked = false;
                        });
                    }
                } else {
                    // Individual group checkbox logic
                    if (e.target.checked) {
                        // Uncheck "All Groups"
                        const allGroupsCheckbox = document.querySelector('.group-checkbox[value=""]');
                        if (allGroupsCheckbox) allGroupsCheckbox.checked = false;
                    }
                }
                this.applyFilters();
            });
        });

        // Select all checkbox
        const selectAllCheckbox = document.getElementById('select-all');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                e.stopPropagation(); // Prevent table sorting
                this.toggleSelectAll(e.target.checked);
            });
            selectAllCheckbox.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent table sorting on click
            });
        }

        // Individual player checkboxes
        document.querySelectorAll('.player-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                e.stopPropagation(); // Prevent table sorting
                this.togglePlayerSelection(e.target.value, e.target.checked);
            });
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent table sorting on click
            });
        });

        // Bulk action buttons
        const bulkAssignBtn = document.getElementById('bulk-assign-btn');
        const compareBtn = document.getElementById('compare-players-btn');

        if (bulkAssignBtn) {
            bulkAssignBtn.addEventListener('click', () => this.handleBulkAssignment());
        }
        if (compareBtn) {
            compareBtn.addEventListener('click', () => this.handlePlayerComparison());
        }
    }

    collectPlayerData() {
        const playerRows = document.querySelectorAll('.player-row');
        this.allPlayers = Array.from(playerRows).map(row => {
            const playerId = row.getAttribute('data-player-id');
            const playerName = row.getAttribute('data-player-name') || '';
            const playerGroupId = row.getAttribute('data-player-group-id') || '';
            const playerGroupName = row.getAttribute('data-player-group-name') || '';
            const playerPosition = row.getAttribute('data-player-position') || '';

            return {
                id: playerId,
                name: playerName.trim(),
                groupId: playerGroupId,
                groupName: playerGroupName,
                position: playerPosition,
                element: row
            };
        });

        // Initialize filteredPlayers to include all players
        this.allPlayers.forEach(player => this.filteredPlayers.add(player.id));
        console.log('Collected player data:', this.allPlayers.length, 'players');
    }

    applyFilters() {
        const nameFilter = document.getElementById('name-filter')?.value?.toLowerCase() || '';

        // Get selected group IDs from checkboxes
        const checkedGroups = Array.from(document.querySelectorAll('.group-checkbox:checked'))
            .map(cb => cb.value)
            .filter(val => val !== ''); // Remove empty value (All Groups)

        const allGroupsSelected = document.querySelector('.group-checkbox[value=""]:checked');

        console.log('Applying filters:', { nameFilter, checkedGroups, allGroupsSelected: !!allGroupsSelected });

        this.filteredPlayers.clear();
        let visibleCount = 0;

        this.allPlayers.forEach(player => {
            // More explicit filtering - only apply filter if it has a value
            let nameMatch = true;
            let groupMatch = true;

            if (nameFilter && nameFilter.trim() !== '') {
                nameMatch = player.name && player.name.toLowerCase().includes(nameFilter);
            }

            // Group filtering logic
            if (!allGroupsSelected && checkedGroups.length > 0) {
                groupMatch = checkedGroups.includes(player.groupId);
            }

            const visible = nameMatch && groupMatch;

            if (visible) {
                this.filteredPlayers.add(player.id);
                player.element.style.display = 'table-row';
                visibleCount++;
            } else {
                player.element.style.display = 'none';
            }
        });

        console.log(`Visible players: ${visibleCount} of ${this.allPlayers.length}`);
        this.updateFilterResults(visibleCount);
        this.updateSelectAllState();
        this.saveFiltersToStorage();
    }

    clearSelection() {
        this.selectedPlayers.clear();

        // Uncheck all checkboxes
        document.querySelectorAll('.player-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        const selectAllCheckbox = document.getElementById('select-all');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        }

        this.updateBulkActions();
    }

    updateFilterResults(visibleCount) {
        const resultsElement = document.getElementById('filter-results');
        if (resultsElement) {
            resultsElement.textContent = `Showing ${visibleCount} of ${this.allPlayers.length} players`;
        }
    }

    toggleSelectAll(checked) {
        const visiblePlayers = this.allPlayers.filter(player => this.filteredPlayers.has(player.id));

        visiblePlayers.forEach(player => {
            const checkbox = document.querySelector(`.player-checkbox[value="${player.id}"]`);
            if (checkbox) {
                checkbox.checked = checked;
                this.togglePlayerSelection(player.id, checked);
            }
        });
    }

    togglePlayerSelection(playerId, selected) {
        if (selected) {
            this.selectedPlayers.add(playerId);
        } else {
            this.selectedPlayers.delete(playerId);
        }

        this.updateSelectAllState();
        this.updateBulkActions();
    }

    updateBulkActions() {
        const selectedCount = this.selectedPlayers.size;

        // Update action button states
        const bulkAssignBtn = document.getElementById('bulk-assign-btn');
        const compareBtn = document.getElementById('compare-players-btn');

        if (bulkAssignBtn) {
            bulkAssignBtn.disabled = selectedCount === 0;
        }
        if (compareBtn) {
            compareBtn.disabled = selectedCount < 2 || selectedCount > 8;
        }

        // Update selection counter
        const selectionCount = document.getElementById('selection-count');
        if (selectionCount) {
            if (selectedCount === 0) {
                selectionCount.textContent = 'Select players to assign to groups or compare (max 8)';
            } else {
                selectionCount.textContent = `${selectedCount} player${selectedCount !== 1 ? 's' : ''} selected`;
            }
        }
    }

    updateSelectAllState() {
        const selectAllCheckbox = document.getElementById('select-all');
        if (!selectAllCheckbox) return;

        const visiblePlayers = this.allPlayers.filter(player => this.filteredPlayers.has(player.id));
        const selectedVisiblePlayers = visiblePlayers.filter(player => this.selectedPlayers.has(player.id));

        if (selectedVisiblePlayers.length === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (selectedVisiblePlayers.length === visiblePlayers.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.indeterminate = true;
        }
    }

    async handleBulkAssignment() {
        const groupId = document.getElementById('bulk-group-select')?.value;
        if (!groupId) {
            return;
        }

        const playerIds = Array.from(this.selectedPlayers);

        try {
            const response = await fetch('/api/players/bulk-assign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    player_ids: playerIds,
                    group_id: groupId === '-1' ? null : groupId,
                    team_id: this.getTeamId()
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.clearSelection();
                location.reload(); // Refresh to show updated groups
            } else {
                const error = await response.json();
                console.error('Assignment error:', error.message);
            }
        } catch (error) {
            console.error('Bulk assignment error:', error);
        }
    }

    handlePlayerComparison() {
        const playerIds = Array.from(this.selectedPlayers);
        if (playerIds.length < 2 || playerIds.length > 8) {
            return;
        }

        // Navigate to comparison page
        const params = new URLSearchParams();
        params.append('team_id', this.getTeamId());
        playerIds.forEach(id => params.append('player_ids', id));

        window.location.href = `/player/compare?${params.toString()}`;
    }

    getTeamId() {
        // Extract team ID from the page - would need to be passed from template
        return document.querySelector('[name="id"]')?.value || '';
    }

    saveFiltersToStorage() {
        const nameFilter = document.getElementById('name-filter')?.value || '';
        const groupFilterElement = document.getElementById('group-filter');
        const selectedGroups = groupFilterElement ?
            Array.from(groupFilterElement.selectedOptions).map(option => option.value) :
            [];

        const filters = {
            name: nameFilter,
            groups: selectedGroups
        };
        localStorage.setItem('player-table-filters', JSON.stringify(filters));
    }

    restoreFiltersFromStorage() {
        const saved = localStorage.getItem('player-table-filters');
        if (!saved) return;

        try {
            const filters = JSON.parse(saved);
            const nameFilter = document.getElementById('name-filter');
            const groupFilter = document.getElementById('group-filter');
            const positionFilter = document.getElementById('position-filter');

            if (nameFilter) nameFilter.value = filters.name || '';
            if (groupFilter) groupFilter.value = filters.group || '';
            if (positionFilter) positionFilter.value = filters.position || '';

            // Apply filters after a short delay to ensure DOM is ready
            setTimeout(() => this.applyFilters(), 100);
        } catch (error) {
            console.warn('Failed to restore filters:', error);
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}
