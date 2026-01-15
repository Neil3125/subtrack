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
        updateCustomerGroupDisplay();

        // Reset title
        const title = document.querySelector('#customerModal .modal-title');
        if (title) title.textContent = 'Create Customer';
        const btn = document.querySelector('#customerModal button[type="submit"]');
        if (btn) btn.textContent = 'Create Customer';

        // Reset form dataset
        if (form) delete form.dataset.itemId;
    }

    // Initialize multi-select displays
    updateCustomerCategoryDisplay();
    updateCustomerGroupDisplay();
};

// ==================== CATEGORY TAGS ====================

window.toggleCustomerCategoryTag = function (element) {
    const id = parseInt(element.dataset.id);
    const name = element.dataset.name;

    const existingIndex = customerModalState.selectedCategories.findIndex(c => c.id === id);

    if (existingIndex >= 0) {
        customerModalState.selectedCategories.splice(existingIndex, 1);
        element.classList.remove('selected');
    } else {
        customerModalState.selectedCategories.push({ id, name });
        element.classList.add('selected');
    }

    updateCustomerCategoryDisplay();
};

window.removeCustomerCategoryChip = function (id) {
    customerModalState.selectedCategories = customerModalState.selectedCategories.filter(c => c.id !== id);

    const dropdown = document.getElementById('customer-categories-dropdown');
    if (dropdown) {
        const item = dropdown.querySelector(`.tags-dropdown-item[data-id="${id}"]`);
        if (item) item.classList.remove('selected');
    }

    updateCustomerCategoryDisplay();
};

window.preselectCustomerCategories = function (categoryIds) {
    customerModalState.selectedCategories = [];

    const dropdown = document.getElementById('customer-categories-dropdown');
    if (dropdown) {
        dropdown.querySelectorAll('.tags-dropdown-item').forEach(el => el.classList.remove('selected'));

        if (Array.isArray(categoryIds)) {
            categoryIds.forEach(id => {
                const item = dropdown.querySelector(`.tags-dropdown-item[data-id="${id}"]`);
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

    if (hiddenInput) {
        hiddenInput.value = customerModalState.selectedCategories.map(c => c.id).join(',');
    }

    if (customerModalState.selectedCategories.length === 0) {
        display.innerHTML = '<span class="categories-placeholder">Click to select...</span>';
    } else {
        customerModalState.selectedCategories.forEach(cat => {
            const tag = document.createElement('div');
            tag.className = 'multi-select-tag';
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

// ==================== GROUP TAGS ====================

window.toggleCustomerGroupTag = function (element) {
    const id = parseInt(element.dataset.id);
    const name = element.dataset.name;

    const existingIndex = customerModalState.selectedGroups.findIndex(g => g.id === id);

    if (existingIndex >= 0) {
        customerModalState.selectedGroups.splice(existingIndex, 1);
        element.classList.remove('selected');
    } else {
        customerModalState.selectedGroups.push({ id, name });
        element.classList.add('selected');
    }

    updateCustomerGroupDisplay();
};

window.removeCustomerGroupChip = function (id) {
    customerModalState.selectedGroups = customerModalState.selectedGroups.filter(g => g.id !== id);

    const dropdown = document.getElementById('customer-groups-dropdown');
    if (dropdown) {
        const item = dropdown.querySelector(`.tags-dropdown-item[data-id="${id}"]`);
        if (item) item.classList.remove('selected');
    }

    updateCustomerGroupDisplay();
};

window.preselectCustomerGroups = function (groupIds) {
    customerModalState.selectedGroups = [];

    const dropdown = document.getElementById('customer-groups-dropdown');
    if (dropdown) {
        dropdown.querySelectorAll('.tags-dropdown-item').forEach(el => el.classList.remove('selected'));

        if (Array.isArray(groupIds)) {
            groupIds.forEach(id => {
                const item = dropdown.querySelector(`.tags-dropdown-item[data-id="${id}"]`);
                if (item) {
                    item.classList.add('selected');
                    customerModalState.selectedGroups.push({
                        id: parseInt(id),
                        name: item.dataset.name || item.textContent.trim()
                    });
                }
            });
        }
    }
    updateCustomerGroupDisplay();
};

function updateCustomerGroupDisplay() {
    const display = document.getElementById('customer-groups-tags');
    const hiddenInput = document.getElementById('customer-group-ids');

    if (!display) return;

    display.innerHTML = '';

    if (hiddenInput) {
        hiddenInput.value = customerModalState.selectedGroups.map(g => g.id).join(',');
    }

    if (customerModalState.selectedGroups.length === 0) {
        display.innerHTML = '<span class="categories-placeholder">Click to select...</span>';
    } else {
        customerModalState.selectedGroups.forEach(grp => {
            const tag = document.createElement('div');
            tag.className = 'multi-select-tag';
            tag.innerHTML = `
              <span>${grp.name}</span>
              <span class="multi-select-tag-remove" onclick="event.stopPropagation(); removeCustomerGroupChip(${grp.id})">×</span>
          `;
            display.appendChild(tag);
        });
    }
}

window.openCustomerGroupSelector = function () {
    const dropdown = document.getElementById('customer-groups-dropdown');
    if (dropdown) dropdown.style.display = 'block';
};

window.closeCustomerGroupSelector = function () {
    const dropdown = document.getElementById('customer-groups-dropdown');
    if (dropdown) dropdown.style.display = 'none';
};

// Close dropdowns when clicking outside
document.addEventListener('click', function (e) {
    if (!e.target.closest('#customer-categories-wrapper')) {
        closeCustomerCategorySelector();
    }
    if (!e.target.closest('#customer-groups-wrapper')) {
        closeCustomerGroupSelector();
    }
});


// ==================== UNIFIED SUBMISSION ====================

window.saveEnhancedCustomer = function (formData, itemId = null) {
    const method = itemId ? 'PUT' : 'POST';
    const url = itemId ? `/api/customers/${itemId}` : '/api/customers';
    const action = itemId ? 'updated' : 'created';

    // Handle category_ids - must be an array
    if (customerModalState.selectedCategories.length > 0) {
        formData.category_ids = customerModalState.selectedCategories.map(c => c.id);
    } else if (typeof formData.category_ids === 'string' && formData.category_ids) {
        formData.category_ids = formData.category_ids.split(',').filter(x => x).map(Number);
    } else {
        formData.category_ids = [];
    }

    // Handle group_ids - must be an array  
    if (customerModalState.selectedGroups.length > 0) {
        formData.group_ids = customerModalState.selectedGroups.map(g => g.id);
    } else if (typeof formData.group_ids === 'string' && formData.group_ids) {
        formData.group_ids = formData.group_ids.split(',').filter(x => x).map(Number);
    } else {
        formData.group_ids = [];
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
                    msg = Array.isArray(msg)
                        ? msg.map(err => `${err.loc ? err.loc.join('.') : 'field'}: ${err.msg}`).join(', ')
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

            setTimeout(() => {
                initEnhancedCustomerModal(isEdit);
            }, 10);
        }
        if (originalOpenModal) originalOpenModal(modalId);
    };
})();
