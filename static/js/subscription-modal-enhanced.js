// ==================== ENHANCED SUBSCRIPTION MODAL - COMPLETE REVAMP ====================

// Global state for the enhanced modal
const subscriptionModalState = {
  customers: [],
  selectedCustomerId: null,
  selectedCustomerName: null,
  selectedCategories: [],
  vendors: [],
  contextMode: false, // true when opened from customer page
  loading: false
};

// ==================== INITIALIZATION ====================

// Initialize when modal opens
window.initEnhancedSubscriptionModal = function (customerId = null, customerName = null, categoryId = null, isEdit = false) {
  console.log('Initializing improved subscription modal', { customerId, customerName, categoryId, isEdit });

  // Reset form ONLY if not in edit mode
  if (!isEdit) {
    document.getElementById('subscription-form').reset();

    // Reset state
    subscriptionModalState.selectedCategories = [];
    subscriptionModalState.contextMode = false;
    subscriptionModalState.selectedCustomerId = null;
    subscriptionModalState.selectedCustomerName = null;
  }

  // Set context mode if customer provided
  if (customerId && customerName) {
    subscriptionModalState.contextMode = true;
    subscriptionModalState.selectedCustomerId = customerId;
    subscriptionModalState.selectedCustomerName = customerName;

    // Update compact customer display
    updateCompactCustomerDisplay(customerName);

    // Load suggestions
    loadSmartSuggestions(customerId);

    // Pre-select category if provided
    if (categoryId) {
      setTimeout(() => {
        selectCategoryTag(categoryId);
      }, 100);
    }
  } else {
    updateCompactCustomerDisplay(null);
  }

  // Initialize categories display
  updateCategoryDisplay();

  // Load customers
  loadEnhancedCustomers();

  // Load vendors for autocomplete
  loadVendors();

  // Close template dropdown when clicking outside
  document.addEventListener('click', function (e) {
    const templateDropdown = document.getElementById('subscription-templates-dropdown');
    const templateBtn = e.target.closest('button[onclick="toggleTemplateDropdown()"]');
    if (templateDropdown && templateDropdown.style.display === 'block' && !templateBtn && !templateDropdown.contains(e.target)) {
      templateDropdown.style.display = 'none';
    }
  });

  // Initialize vendor autocomplete
  initVendorAutocomplete();

  // Initialize collapsible sections
  initCollapsibleSections();
};

// ==================== CUSTOMER DISPLAY & DROPDOWN ====================

function updateCompactCustomerDisplay(customerName) {
  const nameEl = document.getElementById('selected-customer-name');

  if (nameEl) {
    if (customerName) {
      nameEl.textContent = customerName;
      nameEl.classList.remove('placeholder');
    } else {
      nameEl.textContent = 'Select customer...';
      nameEl.classList.add('placeholder');
    }
  }
}

// Toggle the new customer dropdown
window.toggleCustomerDropdown = function () {
  const wrapper = document.getElementById('customer-selector-wrapper');
  const panel = document.getElementById('customer-dropdown-panel');

  if (!wrapper || !panel) return;

  const isOpen = panel.style.display === 'block';

  if (isOpen) {
    panel.style.display = 'none';
    wrapper.classList.remove('open');
  } else {
    panel.style.display = 'block';
    wrapper.classList.add('open');

    // Ensure customer list is visible immediately
    const listEl = document.getElementById('subscription-customer-list');
    const loadingEl = document.getElementById('subscription-customer-loading');

    // If customers already loaded, show list immediately
    if (subscriptionModalState.customers.length > 0 && listEl) {
      listEl.style.display = 'block';
      if (loadingEl) loadingEl.style.display = 'none';
    }

    // Clear any previous search filter
    const searchInput = document.getElementById('subscription-customer-search');
    if (searchInput) {
      searchInput.value = '';
      // Show all customers
      if (listEl) {
        listEl.querySelectorAll('.dropdown-list-item').forEach(item => {
          item.style.display = 'flex';
        });
      }
      setTimeout(() => searchInput.focus(), 100);
    }
  }
};

// Legacy function for backward compatibility
window.toggleCustomerSelector = function () {
  toggleCustomerDropdown();
};

window.clearCustomerContext = function () {
  subscriptionModalState.contextMode = false;
  subscriptionModalState.selectedCustomerId = null;
  subscriptionModalState.selectedCustomerName = null;

  updateCompactCustomerDisplay(null);
  hideSmartSuggestions();

  document.getElementById('subscription-customer-id').value = '';

  // Close customer dropdown
  const panel = document.getElementById('customer-dropdown-panel');
  const wrapper = document.getElementById('customer-selector-wrapper');
  if (panel) panel.style.display = 'none';
  if (wrapper) wrapper.classList.remove('open');
};

// ==================== ENHANCED CUSTOMER DROPDOWN ====================

function loadEnhancedCustomers() {
  subscriptionModalState.loading = true;

  const loadingEl = document.getElementById('subscription-customer-loading');
  const listEl = document.getElementById('subscription-customer-list');
  const emptyEl = document.getElementById('subscription-customer-empty');
  const statusText = document.getElementById('customer-status-text');

  // Show loading state
  if (loadingEl) loadingEl.style.display = 'flex';
  if (listEl) listEl.style.display = 'none';
  if (emptyEl) emptyEl.style.display = 'none';
  if (statusText) statusText.textContent = 'Loading customers...';

  fetch('/api/customers')
    .then(response => response.json())
    .then(customers => {
      subscriptionModalState.customers = customers;
      subscriptionModalState.loading = false;

      // Hide loading
      if (loadingEl) loadingEl.style.display = 'none';

      if (customers.length === 0) {
        if (emptyEl) {
          emptyEl.innerHTML = '<div class="empty-icon">👥</div><div>No customers yet</div><div style="font-size: 12px; margin-top: 4px; color: var(--color-text-tertiary);">Create a customer first</div>';
          emptyEl.style.display = 'block';
        }
        if (statusText) statusText.textContent = 'No customers available';
      } else {
        // IMPORTANT: Show list immediately after loading
        if (listEl) listEl.style.display = 'block';
        renderCustomerList(customers);

        if (statusText) {
          statusText.innerHTML = `<span class="help-icon">✓</span> ${customers.length} customer${customers.length !== 1 ? 's' : ''} available`;
        }
      }
    })
    .catch(error => {
      console.error('Error loading customers:', error);
      subscriptionModalState.loading = false;

      if (loadingEl) loadingEl.style.display = 'none';
      if (emptyEl) {
        emptyEl.innerHTML = '<div class="empty-icon">⚠️</div><div>Error loading customers</div><div style="font-size: 12px; margin-top: 4px;">Please try again</div>';
        emptyEl.style.display = 'block';
      }
      if (statusText) {
        statusText.innerHTML = '<span class="help-icon">⚠️</span> Error loading customers';
      }
    });
}

function renderCustomerList(customers) {
  const listEl = document.getElementById('subscription-customer-list');
  if (!listEl) return;

  listEl.innerHTML = '';

  customers.forEach(customer => {
    const item = document.createElement('div');
    item.className = 'dropdown-list-item';
    item.innerHTML = `
      <span class="trigger-icon">👤</span>
      <span>${customer.name}</span>
    `;

    if (customer.id === subscriptionModalState.selectedCustomerId) {
      item.classList.add('selected');
    }

    item.onclick = () => selectEnhancedCustomer(customer.id, customer.name);
    listEl.appendChild(item);
  });
}

function preselectCustomer(customerId, customerName) {
  subscriptionModalState.selectedCustomerId = customerId;
  subscriptionModalState.selectedCustomerName = customerName;

  // Update hidden input
  document.getElementById('subscription-customer-id').value = customerId;

  // Update trigger display
  const trigger = document.getElementById('subscription-customer-trigger');
  if (trigger) {
    const textEl = trigger.querySelector('.trigger-text');
    if (textEl) {
      textEl.textContent = customerName;
      textEl.classList.remove('placeholder');
    }
  }
}

window.toggleEnhancedDropdown = function (prefix) {
  const trigger = document.getElementById(`${prefix}-trigger`);
  const panel = document.getElementById(`${prefix}-panel`);

  if (!trigger || !panel) return;

  const isOpen = panel.style.display === 'block';

  if (isOpen) {
    panel.style.display = 'none';
    trigger.classList.remove('open');
  } else {
    panel.style.display = 'block';
    trigger.classList.add('open');

    // Focus search input
    const searchInput = panel.querySelector('.dropdown-search-input');
    if (searchInput) {
      setTimeout(() => searchInput.focus(), 100);
    }
  }
};

function selectEnhancedCustomer(customerId, customerName) {
  subscriptionModalState.selectedCustomerId = customerId;
  subscriptionModalState.selectedCustomerName = customerName;

  // Update hidden input
  document.getElementById('subscription-customer-id').value = customerId;

  // Update list selection
  document.querySelectorAll('#subscription-customer-list .dropdown-list-item').forEach(item => {
    item.classList.remove('selected');
  });
  event?.target?.closest('.dropdown-list-item')?.classList.add('selected');

  // Close new customer dropdown
  const panel = document.getElementById('customer-dropdown-panel');
  const wrapper = document.getElementById('customer-selector-wrapper');
  if (panel) panel.style.display = 'none';
  if (wrapper) wrapper.classList.remove('open');

  // Update compact display
  updateCompactCustomerDisplay(customerName);

  // Activate the card border animation briefly
  const customerCard = document.querySelector('.selection-card-customer');
  if (customerCard) {
    customerCard.classList.add('active');
    setTimeout(() => customerCard.classList.remove('active'), 2000);
  }

  // Load suggestions
  loadSmartSuggestions(customerId);
}

window.filterEnhancedDropdown = function (prefix, searchText) {
  const listEl = document.getElementById(`${prefix}-list`);
  if (!listEl) return;

  const items = listEl.querySelectorAll('.dropdown-list-item');
  const searchLower = searchText.toLowerCase();

  let visibleCount = 0;
  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    if (text.includes(searchLower)) {
      item.style.display = 'flex';
      visibleCount++;
    } else {
      item.style.display = 'none';
    }
  });

  // Show/hide empty state
  const emptyEl = document.getElementById(`${prefix}-empty`);
  if (emptyEl) {
    emptyEl.style.display = visibleCount === 0 ? 'block' : 'none';
  }
};

// Close dropdown when clicking outside
document.addEventListener('click', function (e) {
  if (!e.target.closest('.enhanced-dropdown')) {
    document.querySelectorAll('.enhanced-dropdown-panel').forEach(panel => {
      panel.style.display = 'none';
    });
    document.querySelectorAll('.enhanced-dropdown-trigger').forEach(trigger => {
      trigger.classList.remove('open');
    });
  }
});

// ==================== COLLAPSIBLE SECTIONS ====================

function initCollapsibleSections() {
  // Initialize smart suggestions as collapsed
  const suggestionsContent = document.getElementById('smart-suggestions-content');
  const suggestionsToggle = document.getElementById('smart-suggestions-toggle');
  const collapsibleHeader = document.querySelector('.modal-section-collapsible .collapsible-header');

  if (suggestionsContent) {
    suggestionsContent.style.display = 'none';
  }

  if (collapsibleHeader) {
    collapsibleHeader.classList.remove('open');
  }
}

window.toggleSmartSuggestions = function () {
  const content = document.getElementById('smart-suggestions-content');
  if (!content) return;

  const isOpen = content.style.display !== 'none';

  if (isOpen) {
    content.style.display = 'none';
  } else {
    content.style.display = 'block';

    // Load suggestions if not already loaded
    if (subscriptionModalState.selectedCustomerId && !content.dataset.loaded) {
      loadSmartSuggestions(subscriptionModalState.selectedCustomerId);
      content.dataset.loaded = 'true';
    }
  }
};

// ==================== SMART SUGGESTIONS ====================

function loadSmartSuggestions(customerId) {
  const content = document.getElementById('suggestions-content');

  if (!content) return;

  fetch(`/api/subscriptions?customer_id=${customerId}`)
    .then(response => response.json())
    .then(subscriptions => {
      if (!subscriptions || subscriptions.length === 0) {
        content.innerHTML = '<p style="color: var(--color-text-secondary); font-size: 13px;">No suggestions available for this customer</p>';
        return;
      }

      // Extract unique categories and vendors
      const categories = {};
      const vendors = {};

      subscriptions.forEach(sub => {
        if (sub.category_id && sub.category_name) {
          categories[sub.category_id] = sub.category_name;
        }
        if (sub.vendor_name) {
          vendors[sub.vendor_name] = (vendors[sub.vendor_name] || 0) + 1;
        }
      });

      let html = '';

      // Category suggestions
      const categoryIds = Object.keys(categories);
      if (categoryIds.length > 0) {
        html += '<div><strong style="font-size: 12px; color: var(--color-text-secondary); display: block; margin-bottom: 8px;">Frequently used categories:</strong></div>';
        html += '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">';
        categoryIds.forEach(catId => {
          html += `<div class="suggestion-chip" onclick="applySuggestion('category', ${catId}, '${categories[catId]}')">
            <span class="suggestion-chip-label">${categories[catId]}</span>
            <span class="suggestion-chip-action">+ Add</span>
          </div>`;
        });
        html += '</div>';
      }

      // Vendor suggestions
      const sortedVendors = Object.entries(vendors).sort((a, b) => b[1] - a[1]).slice(0, 5);
      if (sortedVendors.length > 0) {
        html += '<div><strong style="font-size: 12px; color: var(--color-text-secondary); display: block; margin-bottom: 8px;">Frequently used vendors:</strong></div>';
        html += '<div style="display: flex; flex-wrap: wrap; gap: 8px;">';
        sortedVendors.forEach(([vendor, count]) => {
          const escapedVendor = vendor.replace(/'/g, "\\'");
          html += `<div class="suggestion-chip" onclick="applySuggestion('vendor', null, '${escapedVendor}')">
            <span class="suggestion-chip-label">${vendor} <span style="color: var(--color-text-tertiary); font-size: 11px;">(${count}×)</span></span>
            <span class="suggestion-chip-action">+ Use</span>
          </div>`;
        });
        html += '</div>';
      }

      if (html) {
        content.innerHTML = html;
      } else {
        content.innerHTML = '<p style="color: var(--color-text-secondary); font-size: 13px;">No suggestions available for this customer</p>';
      }
    })
    .catch(error => {
      console.error('Error loading suggestions:', error);
      content.innerHTML = '<p style="color: var(--color-text-tertiary); font-size: 13px;">Error loading suggestions</p>';
    });
}

function hideSmartSuggestions() {
  const content = document.getElementById('suggestions-content');
  if (content) {
    content.innerHTML = '';
    content.dataset.loaded = 'false';
  }
}

window.applySuggestion = function (type, id, value) {
  if (type === 'category') {
    selectCategoryTag(id);
  } else if (type === 'vendor') {
    const vendorInput = document.getElementById('subscription-vendor-name');
    if (vendorInput) {
      vendorInput.value = value;
      vendorInput.focus();
    }
  }
};

// ==================== VISUAL CATEGORY TAGS ====================

window.openCategorySelector = function () {
  const dropdown = document.getElementById('subscription-categories-dropdown');
  const display = document.getElementById('subscription-categories-tags');
  const container = document.getElementById('subscription-categories-wrapper');

  if (dropdown) {
    // Check if there are any category items
    const items = dropdown.querySelectorAll('.categories-dropdown-item');

    if (items.length === 0) {
      // No categories available - show a message
      const list = dropdown.querySelector('.categories-dropdown-list');
      if (list && list.children.length === 0) {
        list.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--color-text-tertiary);">No categories available.<br><small>Create a category first.</small></div>';
      }
    }

    dropdown.style.display = 'block';
    display?.classList.add('active');
    container?.classList.add('open');

    // Update selected state in dropdown
    updateCategoryDropdownSelection();
  }
};

window.closeCategorySelector = function () {
  const dropdown = document.getElementById('subscription-categories-dropdown');
  const display = document.getElementById('subscription-categories-tags');
  const container = document.getElementById('subscription-categories-wrapper');

  if (dropdown) {
    dropdown.style.display = 'none';
    display?.classList.remove('active');
    container?.classList.remove('open');
  }
};

function updateCategoryDropdownSelection() {
  const dropdown = document.getElementById('subscription-categories-dropdown');
  if (!dropdown) return;

  const items = dropdown.querySelectorAll('.categories-dropdown-item, .tags-dropdown-item');
  const selectedIds = subscriptionModalState.selectedCategories.map(cat => cat.id);

  items.forEach(item => {
    const itemId = parseInt(item.dataset.id);
    if (selectedIds.includes(itemId)) {
      item.classList.add('selected');
    } else {
      item.classList.remove('selected');
    }
  });
}

window.toggleCategoryTag = function (element) {
  const categoryId = parseInt(element.dataset.id);
  const categoryName = element.dataset.name;

  if (element.classList.contains('selected')) {
    // Deselect
    element.classList.remove('selected');
    removeCategoryFromSelection(categoryId);
  } else {
    // Select
    element.classList.add('selected');
    addCategoryToSelection(categoryId, categoryName);
  }

  // Update display immediately
  updateCategoryDisplay();
};

function selectCategoryTag(categoryId) {
  // Try both selectors for compatibility, scoped to subscription dropdown
  const dropdown = document.getElementById('subscription-categories-dropdown');
  if (!dropdown) return;

  const item = dropdown.querySelector(`.categories-dropdown-item[data-id="${categoryId}"]`) ||
    dropdown.querySelector(`.tags-dropdown-item[data-id="${categoryId}"]`);
  if (item && !item.classList.contains('selected')) {
    toggleCategoryTag(item);
  }
}

function addCategoryToSelection(categoryId, categoryName) {
  subscriptionModalState.selectedCategories.push({ id: categoryId, name: categoryName });
  updateCategoryDisplay();
}

function removeCategoryFromSelection(categoryId) {
  subscriptionModalState.selectedCategories = subscriptionModalState.selectedCategories.filter(
    cat => cat.id !== categoryId
  );
  updateCategoryDisplay();
}

window.removeCategoryChip = function (categoryId) {
  // Try both selectors for compatibility
  const item = document.querySelector(`.categories-dropdown-item[data-id="${categoryId}"]`) ||
    document.querySelector(`.tags-dropdown-item[data-id="${categoryId}"]`);
  if (item) {
    item.classList.remove('selected');
  }
  removeCategoryFromSelection(categoryId);
};

// Pre-select multiple categories (for editing subscriptions)
window.preselectSubscriptionCategories = function (categoryIds) {
  if (!categoryIds || categoryIds.length === 0) return;

  // Reset selected categories
  subscriptionModalState.selectedCategories = [];

  // Get all category dropdown items
  const allCategoryItems = document.querySelectorAll('.categories-dropdown-item');

  // Build a map of category items
  const categoryMap = new Map();
  allCategoryItems.forEach(item => {
    const id = parseInt(item.dataset.id);
    const name = item.dataset.name;
    if (id && name) {
      categoryMap.set(id, { id, name, element: item });
    }
  });

  // Convert categoryIds to array if needed
  const ids = Array.isArray(categoryIds) ? categoryIds : [categoryIds];

  // Pre-select each category
  ids.forEach(categoryId => {
    const id = parseInt(categoryId);
    const category = categoryMap.get(id);

    if (category) {
      // Mark as selected in dropdown
      category.element.classList.add('selected');

      // Add to selectedCategories state
      subscriptionModalState.selectedCategories.push({
        id: category.id,
        name: category.name
      });
    }
  });

  // Update the display
  updateCategoryDisplay();

  console.log('Pre-selected categories:', subscriptionModalState.selectedCategories);
};

function updateCategoryDisplay() {
  const display = document.getElementById('subscription-categories-tags');
  const idsInput = document.getElementById('subscription-category-ids');
  const idInput = document.getElementById('subscription-category-id');

  if (!display) {
    return;
  }

  display.innerHTML = '';

  // SINGLE SOURCE OF TRUTH: subscriptionModalState.selectedCategories
  // Get the category IDs for the hidden inputs (backup for form serialization)
  const ids = subscriptionModalState.selectedCategories.map(cat => cat.id);

  // Always update hidden inputs to stay in sync (backup for form serialization)
  if (idsInput) {
    idsInput.value = ids.join(',');
  }

  if (idInput) {
    idInput.value = ids[0] || '';
  }

  if (subscriptionModalState.selectedCategories.length === 0) {
    display.innerHTML = '<span class="categories-placeholder">Click to select categories...</span>';
  } else {
    // Limit visible chips to prevent overflow
    const maxVisible = 3;
    const categoriesToShow = subscriptionModalState.selectedCategories.slice(0, maxVisible);
    const remainingCount = subscriptionModalState.selectedCategories.length - maxVisible;

    categoriesToShow.forEach(cat => {
      const tag = document.createElement('div');
      tag.className = 'category-tag';
      tag.innerHTML = `
        <span>${cat.name}</span>
        <span class="category-tag-remove" onclick="event.stopPropagation(); removeCategoryChip(${cat.id})">×</span>
      `;
      display.appendChild(tag);
    });

    // Show "+X more" if there are more categories
    if (remainingCount > 0) {
      const moreTag = document.createElement('div');
      moreTag.className = 'category-tag category-tag-more';
      moreTag.innerHTML = `+${remainingCount} more`;
      moreTag.style.cursor = 'pointer';
      moreTag.onclick = () => openCategorySelector();
      display.appendChild(moreTag);
    }
  }
}

// ==================== VENDOR AUTOCOMPLETE ====================

// ==================== VENDOR AUTOCOMPLETE ====================

function loadVendors() {
  // Common vendors to seed (ESET, Adobe, etc.)
  const seededVendors = [
    "Netflix", "Spotify", "Apple", "Google", "AWS", "Microsoft",
    "Adobe", "ESET", "CrowdStrike", "Palo Alto Networks",
    "Slack", "Zoom", "Atlassian", "GitHub", "DigitalOcean",
    "Heroku", "Vercel", "Netlify", "Figma", "Canva",
    "Dropbox", "Box", "Salesforce", "HubSpot", "Zendesk",
    "Intercom", "Mailchimp", "SendGrid", "Twilio", "Stripe"
  ];

  // Fetch unique vendors from subscriptions
  fetch('/api/subscriptions')
    .then(response => response.json())
    .then(subscriptions => {
      const vendorSet = new Set(seededVendors); // Start with seeds
      subscriptions.forEach(sub => {
        if (sub.vendor_name) {
          vendorSet.add(sub.vendor_name);
        }
      });
      subscriptionModalState.vendors = Array.from(vendorSet).sort();
    })
    .catch(error => {
      console.error('Error loading vendors:', error);
      subscriptionModalState.vendors = seededVendors.sort();
    });
}

// ==================== TEMPLATES LOGIC ====================

// Templates logic removed - moved to templates-manager.js

window.applySubscriptionTemplate = function (vendor, plan, cost, currency) {
  // Auto-fill form fields
  const vendorInput = document.getElementById('subscription-vendor-name');
  const planInput = document.querySelector('input[name="plan_name"]');
  const costInput = document.querySelector('input[name="cost"]');
  const currencySelect = document.querySelector('select[name="currency"]');

  if (vendorInput) vendorInput.value = vendor;
  if (planInput) planInput.value = plan;
  if (costInput) costInput.value = cost;
  if (currencySelect) currencySelect.value = currency;

  // Close dropdown
  const dropdown = document.getElementById('subscription-templates-dropdown');
  if (dropdown) dropdown.style.display = 'none';

  // Show feedback
  showToast(`Applied template: ${vendor}`, 'success');
};

function initVendorAutocomplete() {
  const vendorInput = document.getElementById('subscription-vendor-name');
  if (!vendorInput || vendorInput._vendorAutocomplete) return;

  // Use the existing SmartAutocomplete class
  const autocomplete = new SmartAutocomplete(vendorInput, {
    dataSource: subscriptionModalState.vendors,
    minChars: 1,
    maxResults: 10,
    placeholder: 'e.g., AWS, Netflix, Adobe',
    emptyMessage: 'No vendors found - type to add new',
    highlightMatches: true,
    showRecentFirst: true
  });

  vendorInput._vendorAutocomplete = autocomplete;

  // Update data source when vendors are loaded
  const checkVendors = setInterval(() => {
    if (subscriptionModalState.vendors.length > 0) {
      autocomplete.updateDataSource(subscriptionModalState.vendors);
      clearInterval(checkVendors);
    }
  }, 500);
}

// ==================== OVERRIDE EXISTING FUNCTIONS ====================

// Override the old openModal function for subscription modal
const originalOpenModal = window.openModal;
window.openModal = function (modalId) {
  if (modalId === 'subscriptionModal') {
    const form = document.querySelector('#subscriptionModal form');
    // Check if we are in edit mode (form has an item ID)
    const isEdit = form && form.dataset.itemId && form.dataset.itemId !== '';
    initEnhancedSubscriptionModal(null, null, null, isEdit);
  }
  if (originalOpenModal) {
    originalOpenModal(modalId);
  } else {
    // Fallback if original not defined yet
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'flex';
  }
};

// Update the openSubscriptionModalForCustomer function
window.openSubscriptionModalForCustomer = function (categoryId, customerId, customerName) {
  // Open modal first
  originalOpenModal('subscriptionModal');

  // Then initialize with customer context
  setTimeout(() => {
    initEnhancedSubscriptionModal(customerId, customerName, categoryId);
  }, 100);
};

// Close dropdowns when clicking outside (updated for new layout)
document.addEventListener('click', function (e) {
  // Close customer dropdown when clicking outside
  if (!e.target.closest('.customer-selector-wrapper') && !e.target.closest('.customer-dropdown-panel')) {
    const panel = document.getElementById('customer-dropdown-panel');
    const wrapper = document.getElementById('customer-selector-wrapper');
    if (panel) {
      panel.style.display = 'none';
    }
    if (wrapper) {
      wrapper.classList.remove('open');
    }
  }

  // Close categories dropdown when clicking outside
  if (!e.target.closest('.categories-chips-container') && !e.target.closest('.categories-dropdown')) {
    const dropdown = document.getElementById('subscription-categories-dropdown');
    const display = document.getElementById('subscription-categories-tags');
    const container = document.getElementById('subscription-categories-wrapper');
    if (dropdown) {
      dropdown.style.display = 'none';
    }
    if (display) {
      display.classList.remove('active');
    }
    if (container) {
      container.classList.remove('open');
    }
  }

  // Close enhanced dropdowns when clicking outside
  if (!e.target.closest('.enhanced-dropdown')) {
    document.querySelectorAll('.enhanced-dropdown-panel').forEach(panel => {
      panel.style.display = 'none';
    });
    document.querySelectorAll('.enhanced-dropdown-trigger').forEach(trigger => {
      trigger.classList.remove('open');
    });
  }
});

console.log('✅ Enhanced Subscription Modal loaded successfully');

// ==================== UNIFIED SUBMISSION HANDLER ====================

// Save subscription (Create or Update)
window.saveEnhancedSubscription = function (formData, itemId = null) {
  const method = itemId ? 'PUT' : 'POST';
  const url = itemId ? `/api/subscriptions/${itemId}` : '/api/subscriptions';
  const action = itemId ? 'updated' : 'created';

  // Ensure category_ids are included if not present in formData
  if (!formData.category_ids && subscriptionModalState.selectedCategories.length > 0) {
    formData.category_ids = subscriptionModalState.selectedCategories.map(c => c.id);
  } else if (typeof formData.category_ids === 'string') {
    // Convert comma-separated string to array of numbers
    formData.category_ids = formData.category_ids.split(',').filter(id => id).map(Number);
  }

  // Handle cost
  if (formData.cost) formData.cost = parseFloat(formData.cost);

  // Handle customer_id (ensure integer)
  if (formData.customer_id) {
    if (typeof formData.customer_id === 'string') {
      // Remove any non-numeric chars just in case, though basic parsing works
      const parsed = parseInt(formData.customer_id, 10);
      if (!isNaN(parsed)) {
        formData.customer_id = parsed;
      } else {
        // Leave as is, let backend error or handle validation
      }
    }
    // If number, it's fine
  } else if (!formData.customer_id && subscriptionModalState.selectedCustomerId) {
    // Fallback to state if form field empty
    formData.customer_id = parseInt(subscriptionModalState.selectedCustomerId, 10);
  }

  // Make the API request
  fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
  })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          let errorMsg = 'Failed to save subscription';
          if (err.detail) {
            if (typeof err.detail === 'string') {
              errorMsg = err.detail;
            } else if (Array.isArray(err.detail)) {
              // Handle FastAPIs validation error array
              errorMsg = err.detail.map(e => {
                const field = e.loc[e.loc.length - 1]; // get the field name
                return `${field}: ${e.msg}`;
              }).join('\n');
            } else if (typeof err.detail === 'object') {
              errorMsg = JSON.stringify(err.detail);
            }
          }
          throw new Error(errorMsg);
        });
      }
      return response.json();
    })
    .then(data => {
      showToast(`Subscription ${action} successfully`, 'success');
      closeModal('subscriptionModal');
      // Reload page or update UI
      setTimeout(() => window.location.reload(), 500);
    })
    .catch(error => {
      showToast(`Error: ${error.message}`, 'error');
      console.error('Error saving subscription:', error);
    });
};
