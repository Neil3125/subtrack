
// ==================== VENDOR AUTOCOMPLETE (TYPEAHEAD) ====================

// Load vendor stats AND templates
window.loadVendors = function () {
    const p1 = fetch('/api/subscriptions/stats/vendors').then(r => r.json());
    const p2 = fetch('/api/templates').then(r => r.json());

    Promise.all([p1, p2])
        .then(([stats, templates]) => {
            // 1. Process Templates (High Priority)
            const templateItems = templates.map(t => ({
                type: 'template',
                name: t.vendor_name,
                plan_name: t.plan_name,
                cost: t.cost,
                currency: t.currency,
                billing_cycle: t.billing_cycle,
                category_id: t.category_id,
                sortKey: t.vendor_name.toLowerCase()
            }));

            // 2. Process History Stats (Low Priority)
            // Only add if not already covered by a template with same vendor name? 
            // User says "search options". Maybe show both?
            // "Netflix (Template: Premium)" vs "Netflix (History)"
            const statItems = stats.map(s => ({
                type: 'history',
                name: s.name,
                cost: s.cost,
                currency: s.currency,
                billing_cycle: s.billing_cycle,
                category_id: s.category_id,
                sortKey: s.name.toLowerCase()
            }));

            // Merge: We want templates to show up.
            subscriptionModalState.vendorOptions = [...templateItems, ...statItems];
            subscriptionModalState.vendors = [...new Set([...templates.map(t => t.vendor_name), ...stats.map(s => s.name)])];
        })
        .catch(err => console.error('Error loading vendor data:', err));
};

// ... initVendorAutocomplete ...
// Inside the input event listener:

// Filter vendorOptions instead of vendorStats
const val = e.target.value.toLowerCase();
const matches = (subscriptionModalState.vendorOptions || [])
    .filter(v => v.name.toLowerCase().includes(val))
    .slice(0, 8); // Limit to 8

if (matches.length > 0) {
    suggestionsBox.innerHTML = '';
    matches.forEach(item => {
        // ... create element ...
        const div = document.createElement('div');
        // styling...

        let label = item.name;
        let subLabel = '';
        let badge = '';

        if (item.type === 'template') {
            badge = `<span class="badge" style="font-size: 10px; background: var(--color-primary-bg); color: var(--color-primary); margin-left: 6px;">Template</span>`;
            if (item.plan_name) label += ` - ${item.plan_name}`;
        } else {
            badge = `<span class="badge" style="font-size: 10px; background: var(--color-bg-secondary); color: var(--color-text-tertiary); margin-left: 6px;">History</span>`;
        }

        if (item.cost) subLabel += `${item.currency || '$'}${item.cost}`;
        if (item.billing_cycle) subLabel += ` / ${item.billing_cycle.split('.')[1] || item.billing_cycle}`;

        div.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <div>
                <span style="font-weight: 500;">${label}</span>
                ${badge}
            </div>
            <span style="font-size: 11px; color: var(--color-text-secondary);">${subLabel}</span>
          </div>
        `;

        div.onmousedown = (e) => {
            e.preventDefault();
            selectVendorSuggestion(item);
        };
        suggestionsBox.appendChild(div);
    });
    suggestionsBox.style.display = 'block';
}
