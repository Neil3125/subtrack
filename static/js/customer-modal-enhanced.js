// ==================== ENHANCED CUSTOMER MODAL ====================

const customerModalState = {
    selectedCategories: [],
    selectedGroups: [],
    isEdit: false
};

// ==================== INITIALIZATION ====================

window.initEnhancedCustomerModal = function (isEdit = false) {
    customerModalState.isEdit = isEdit;

    if (!isEdit) {
        // Reset form and state
        const form = document.querySelector('#customerModal form');
        if (form) form.reset();

        customerModalState.selectedCategories = [];
        customerModalState.selectedGroups = [];

        // Reset display
        updateCustomerCategoryDisplay();

        // Reset title
        const title = document.querySelector('#customerModal .modal-title');
        if (title) title.textContent = 'Create Customer';
        const btn = document.querySelector('#customerModal button[type="submit"]');
        if (btn) btn.textContent = 'Create Customer';

        // Reset form dataset
        if (form) delete form.dataset.itemId;

        // Clear groups
        const groupContainer = document.getElementById('customer-groups-container');
        if (groupContainer) {
            groupContainer.innerHTML = '<div class="multi-select-placeholder">Select a category first, or groups will load automatically</div>';
        }
    }

    // Initialize multi-select displays
    updateCustomerCategoryDisplay();
};

// ==================== CATEGORY TAGS ====================

window.toggleCustomerCategoryTag = function (element) {
    const id = parseInt(element.dataset.id);
    const name = element.dataset.name;

    const existingIndex = customerModalState.selectedCategories.findIndex(c => c.id === id);

    if (existingIndex >= 0) {
        // Remove
        customerModalState.selectedCategories.splice(existingIndex, 1);
        element.classList.remove('selected');
    } else {
        // Add
        customerModalState.selectedCategories.push({ id, name });
        element.classList.add('selected');
    }

    updateCustomerCategoryDisplay();
};

window.removeCustomerCategoryChip = function (id) {
    customerModalState.selectedCategories = customerModalState.selectedCategories.filter(c => c.id !== id);

    // Update dropdown state
    const dropdown = document.getElementById('customer-categories-dropdown');
    if (dropdown) {
        const item = dropdown.querySelector(`.customer-category-item[data-id="${id}"], .tags-dropdown-item[data-id="${id}"]`);
        if (item) item.classList.remove('selected');
    }

    updateCustomerCategoryDisplay();
};

window.preselectCustomerCategories = function (categoryIds) {
    // Clear current
    customerModalState.selectedCategories = [];

    // Clear selection in UI
    const dropdown = document.getElementById('customer-categories-dropdown');
    if (dropdown) {
        dropdown.querySelectorAll('.tags-dropdown-item, .customer-category-item').forEach(el => el.classList.remove('selected'));

        // Find names and select
        if (Array.isArray(categoryIds)) {
            categoryIds.forEach(id => {
                const item = dropdown.querySelector(`.tags-dropdown-item[data-id="${id}"], .customer-category-item[data-id="${id}"]`);
                if (item) {
                    item.classList.add('selected');
                    customerModalState.selectedCategories.push({
                        id: parseInt(id),
                        name: item.dataset.name || item.textContent.trim()
                    });
                }
            });
        }
    }
    updateCustomerCategoryDisplay();
};

function updateCustomerCategoryDisplay() {
    const display = document.getElementById('customer-categories-tags');
    const hiddenInput = document.getElementById('customer-category-ids');

    if (!display) return;

    display.innerHTML = '';

    // Update hidden input
    if (hiddenInput) {
        hiddenInput.value = customerModalState.selectedCategories.map(c => c.id).join(',');
    }

    if (customerModalState.selectedCategories.length === 0) {
        display.innerHTML = '<span class="categories-placeholder" style="color: var(--color-text-tertiary); font-size: 13px;">Click to select...</span>';
    } else {
        customerModalState.selectedCategories.forEach(cat => {
            const tag = document.createElement('div');
            tag.className = 'multi-select-tag'; // Match Subscription style
            tag.innerHTML = `
              <span>${cat.name}</span>
              <span class="multi-select-tag-remove" onclick="event.stopPropagation(); removeCustomerCategoryChip(${cat.id})">×</span>
          `;
            display.appendChild(tag);
        });
    }
}

window.openCustomerCategorySelector = function () {
    const dropdown = document.getElementById('customer-categories-dropdown');
    if (dropdown) dropdown.style.display = 'block';
};

window.closeCustomerCategorySelector = function () {
    const dropdown = document.getElementById('customer-categories-dropdown');
    if (dropdown) dropdown.style.display = 'none';
};

// Close when clicking outside
document.addEventListener('click', function (e) {
    if (!e.target.closest('#customer-categories-wrapper')) { // Updated ID match
        closeCustomerCategorySelector();
    }
});


// ==================== UNIFIED SUBMISSION ====================

window.saveEnhancedCustomer = function (formData, itemId = null) {
    const method = itemId ? 'PUT' : 'POST';
    const url = itemId ? `/api/customers/${itemId}` : '/api/customers';
    const action = itemId ? 'updated' : 'created';

    // Ensure category_ids 
    if (!formData.category_ids && customerModalState.selectedCategories.length > 0) {
        formData.category_ids = customerModalState.selectedCategories.map(c => c.id);
    } else if (typeof formData.category_ids === 'string') {
        formData.category_ids = formData.category_ids.split(',').filter(x => x).map(Number);
    }

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
        .then(response => {
            if (!response.ok) return response.json().then(e => {
                let msg = e.detail || 'Error';
                if (typeof msg === 'object') {
                    // Handle array of errors (e.g. FastAPI validation) or object
                    msg = Array.isArray(msg)
                        ? msg.map(err => `${err.loc.join('.')}: ${err.msg}`).join('\n')
                        : JSON.stringify(msg);
                }
                throw new Error(msg);
            });
            return response.json();
        })
        .then(data => {
            showToast(`Customer ${action} successfully`, 'success');
            closeModal('customerModal');
            setTimeout(() => window.location.reload(), 500);
        })
        .catch(error => {
            console.error('Customer save error:', error);
            showToast(error.message, 'error');
        });
};

// ==================== MODAL OVERRIDE ====================
(function () {
    const originalOpenModal = window.openModal;
    window.openModal = function (modalId) {
        if (modalId === 'customerModal') {
            const form = document.querySelector('#customerModal form');
            const isEdit = form && form.dataset.itemId && form.dataset.itemId !== '';

            // Should initiate if strictly opening (Create mode mostly)
            // or ensuring Edit mode state is clean
            setTimeout(() => {
                initEnhancedCustomerModal(isEdit);
            }, 10);
        }
        if (originalOpenModal) originalOpenModal(modalId);
    };
})();
