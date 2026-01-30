/**
 * Table Sorting Utility
 * Allows HTML tables to be sorted by clicking headers.
 * Supports: Text, Numbers, Custom sort values (data-sort-value).
 */

const TableSort = {
    init() {
        document.querySelectorAll('th[data-sortable="true"]').forEach(th => {
            th.addEventListener('click', () => {
                const table = th.closest('table');
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const index = Array.from(th.parentNode.children).indexOf(th);
                const type = th.dataset.sortType || 'text'; // text, number, date
                const isAsc = th.classList.contains('sort-asc');

                // Reset other headers
                table.querySelectorAll('th').forEach(h => {
                    if (h !== th) {
                        h.classList.remove('sort-asc', 'sort-desc');
                    }
                });

                // Toggle click
                if (isAsc) {
                    th.classList.remove('sort-asc');
                    th.classList.add('sort-desc');
                } else {
                    th.classList.remove('sort-desc');
                    th.classList.add('sort-asc');
                }

                // Sort rows
                const direction = isAsc ? -1 : 1;

                rows.sort((a, b) => {
                    const aCell = a.children[index];
                    const bCell = b.children[index];

                    let aVal = aCell.getAttribute('data-sort-value') || aCell.innerText.trim();
                    let bVal = bCell.getAttribute('data-sort-value') || bCell.innerText.trim();

                    if (type === 'number') {
                        aVal = parseFloat(aVal) || 0;
                        bVal = parseFloat(bVal) || 0;
                        return (aVal - bVal) * direction;
                    }

                    if (type === 'date') {
                        // Attempt to parse if not sort value
                        aVal = new Date(aVal).getTime() || 0;
                        bVal = new Date(bVal).getTime() || 0;
                        return (aVal - bVal) * direction;
                    }

                    // Default text sort
                    return aVal.localeCompare(bVal, undefined, { numeric: true, sensitivity: 'base' }) * direction;
                });

                // Re-append sorted rows
                rows.forEach(row => tbody.appendChild(row));

                // Update indicator
                this.updateIndicators(th, !isAsc);
            });

            // Add cursor pointer
            th.style.cursor = 'pointer';
            th.style.userSelect = 'none';
            th.title = 'Click to sort';

            // Add indicator span if not present
            if (!th.querySelector('.sort-indicator')) {
                const span = document.createElement('span');
                span.className = 'sort-indicator';
                span.style.marginLeft = '5px';
                span.style.fontSize = '0.8em';
                span.style.color = 'var(--color-text-secondary)';
                span.innerHTML = '↕';
                th.appendChild(span);
            }
        });
    },

    updateIndicators(th, isAsc) {
        th.closest('tr').querySelectorAll('.sort-indicator').forEach(span => span.innerHTML = '↕');
        const currentSpan = th.querySelector('.sort-indicator');
        if (currentSpan) {
            currentSpan.innerHTML = isAsc ? '▲' : '▼';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    TableSort.init();
});
