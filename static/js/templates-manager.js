/**
 * Template Manager Component
 * Handles the Side Panel UI for Managing & Applying Templates
 */

const TemplateManager = {
    state: {
        templates: [],
        history: [],
        isLoading: false,
        activeTab: 'saved' // 'saved' or 'history'
    },

    init() {
        // Expose global function to open panel
        window.openTemplatesPanel = this.openPanel.bind(this);
    },

    openPanel() {
        const content = this.renderPanel();
        window.openSidePanel(content, 'Subscription Templates');

        // Attach event listeners after rendering
        this.attachListeners();

        // Load data
        this.loadData();
    },

    renderPanel() {
        return `
            <div class="template-manager-container">
                <div class="template-tabs">
                    <div class="template-tab ${this.state.activeTab === 'saved' ? 'active' : ''}" data-tab="saved">My Templates</div>
                    <div class="template-tab ${this.state.activeTab === 'history' ? 'active' : ''}" data-tab="history">History</div>
                </div>
                
                <div class="template-content">
                    <div id="templates-list-container" class="templates-list">
                        <div class="panel-loading">Loading...</div>
                    </div>
                </div>
                
                <div class="template-actions">
                     ${this.state.activeTab === 'saved' ?
                `<button class="btn btn-primary btn-full" onclick="TemplateManager.saveCurrentAsTemplate()">
                            + Save Current Form as Template
                         </button>` : ''}
                </div>
            </div>
        `;
    },

    attachListeners() {
        const container = document.getElementById('side-panel');
        if (!container) return;

        const tabs = container.querySelectorAll('.template-tab');
        tabs.forEach(tab => {
            tab.onclick = () => {
                this.state.activeTab = tab.dataset.tab;
                // Re-render only the content part or just toggle visibility
                // For simplicity, we re-open/re-render the panel content
                // But creating a proper 'switchTab' method is better
                this.switchTab(tab.dataset.tab);
            };
        });
    },

    switchTab(tabName) {
        this.state.activeTab = tabName;

        // Update tab UI
        document.querySelectorAll('.template-tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tabName);
        });

        // Update Footer Button
        const actionsContainer = document.querySelector('.template-actions');
        if (actionsContainer) {
            actionsContainer.innerHTML = tabName === 'saved' ?
                `<button class="btn btn-primary btn-full" onclick="TemplateManager.saveCurrentAsTemplate()">
                    + Save Current Form as Template
                 </button>` : '';
        }

        // Refresh List
        this.renderList();
    },

    loadData() {
        this.state.isLoading = true;

        // Parallel fetch
        Promise.all([
            fetch('/api/templates').then(r => r.json()),
            fetch('/api/subscriptions/templates/all').then(r => r.json())
        ]).then(([saved, history]) => {
            this.state.templates = saved || [];
            this.state.history = history || [];
            this.state.isLoading = false;
            this.renderList();
        }).catch(err => {
            console.error(err);
            this.state.isLoading = false;
            document.getElementById('templates-list-container').innerHTML =
                '<div class="error-state">Failed to load templates</div>';
        });
    },

    renderList() {
        const container = document.getElementById('templates-list-container');
        if (!container) return;

        const data = this.state.activeTab === 'saved' ? this.state.templates : this.state.history;

        if (data.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📂</div>
                    <div class="empty-text">
                        ${this.state.activeTab === 'saved' ? 'No saved templates yet' : 'No history available'}
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = data.map(item => this.renderItem(item)).join('');
    },

    renderItem(item) {
        const isSaved = this.state.activeTab === 'saved';
        // Normalize fields
        const vendor = item.vendor_name || 'Unknown Vendor';
        const plan = item.plan_name || '';
        const cost = item.cost ? `${item.currency || 'USD'} ${item.cost}` : '';
        const name = isSaved ? item.name : vendor; // History uses vendor as main label

        return `
            <div class="template-item">
                <div class="template-info" onclick="TemplateManager.apply('${encodeURIComponent(JSON.stringify(item))}', ${isSaved})">
                    <div class="template-name">${name}</div>
                    <div class="template-details">
                        ${vendor} ${plan ? `• ${plan}` : ''}
                    </div>
                    <div class="template-cost">${cost}</div>
                </div>
                ${isSaved ? `
                    <div class="template-item-actions">
                        <button class="btn-icon danger" onclick="TemplateManager.deleteTemplate(${item.id}, event)">🗑️</button>
                    </div>
                ` : ''}
            </div>
        `;
    },

    apply(itemStr, isSaved) {
        try {
            const item = JSON.parse(decodeURIComponent(itemStr));

            // Map fields to form
            const mapping = {
                'subscription-vendor-name': item.vendor_name,
                'subscription-plan-name': item.plan_name || '', // Helper to find by name attrib if id missing
                'cost': item.cost,
                'currency': item.currency,
                'billing_cycle': item.billing_cycle,
                'notes': item.notes
            };

            // 1. Fill basic inputs
            document.getElementById('subscription-vendor-name').value = item.vendor_name || '';

            const costInput = document.querySelector('input[name="cost"]');
            if (costInput) costInput.value = item.cost || '';

            const currencySelect = document.querySelector('select[name="currency"]');
            if (currencySelect && item.currency) currencySelect.value = item.currency;

            const planInput = document.querySelector('input[name="plan_name"]');
            if (planInput) planInput.value = item.plan_name || '';

            const cycleSelect = document.querySelector('select[name="billing_cycle"]');
            if (cycleSelect && item.billing_cycle) cycleSelect.value = item.billing_cycle;

            const notesInput = document.querySelector('textarea[name="notes"]');
            if (notesInput && item.notes) notesInput.value = item.notes;

            // 2. Handle Category (if present)
            if (item.category_id && window.selectCategoryTag) {
                // Clear existing first
                if (window.subscriptionModalState) window.subscriptionModalState.selectedCategories = [];
                window.selectCategoryTag(item.category_id);
            }

            // 3. Feedback
            showToast(`Applied ${isSaved ? 'template' : 'history'}: ${item.vendor_name}`, 'success');

            // 4. Close panel (optional, maybe user wants to keep browsing? No, usually apply = done)
            if (window.closeSidePanel) window.closeSidePanel();

        } catch (e) {
            console.error("Error applying template", e);
            showToast("Error applying template", "error");
        }
    },

    saveCurrentAsTemplate() {
        // Gather form data
        const vendor = document.getElementById('subscription-vendor-name').value;
        if (!vendor) {
            showToast("Please enter at least a Vendor Name", "warning");
            return;
        }

        const cost = document.querySelector('input[name="cost"]').value;
        const currency = document.querySelector('select[name="currency"]').value;
        const plan = document.querySelector('input[name="plan_name"]').value;
        const cycle = document.querySelector('select[name="billing_cycle"]').value;
        const notes = document.querySelector('textarea[name="notes"]').value;

        // Get category (single for now)
        let catId = null;
        if (window.subscriptionModalState && window.subscriptionModalState.selectedCategories.length > 0) {
            catId = window.subscriptionModalState.selectedCategories[0].id;
        }

        // Prompt for name
        const name = prompt("Enter a name for this template:", `${vendor} ${plan || 'Standard'}`);
        if (!name) return;

        const payload = {
            name,
            vendor_name: vendor,
            plan_name: plan,
            cost: cost ? parseFloat(cost) : null,
            currency,
            billing_cycle: cycle,
            category_id: catId,
            notes
        };

        // Send API
        fetch('/api/templates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(r => {
                if (!r.ok) throw new Error("Failed to save");
                return r.json();
            })
            .then(newTemplate => {
                showToast("Template saved!", "success");
                this.state.templates.push(newTemplate);
                this.renderList();
            })
            .catch(err => {
                console.error(err);
                showToast("Error saving template", "error");
            });
    },

    deleteTemplate(id, event) {
        event.stopPropagation(); // prevent apply click
        if (!confirm("Delete this template?")) return;

        fetch(`/api/templates/${id}`, { method: 'DELETE' })
            .then(r => {
                if (!r.ok) throw new Error("Failed");
                this.state.templates = this.state.templates.filter(t => t.id !== id);
                this.renderList();
                showToast("Template deleted", "success");
            })
            .catch(err => showToast("Error deleting template", "error"));
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    TemplateManager.init();
});
