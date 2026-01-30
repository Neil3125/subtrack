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

// ==================== CUSTOMER SELECTION (CARD LOGIC) ====================

// Toggle the customer dropdown (Card Click)
window.toggleSubscriptionCustomerDropdown = function () {
  const dropdown = document.getElementById('subscription-customer-dropdown');
  const display = document.getElementById('subscription-customer-display');
  const wrapper = document.getElementById('subscription-customer-wrapper');
  const arrow = display?.querySelector('.customer-selected-arrow');

  if (!dropdown) return;

  const isOpen = dropdown.style.display === 'block';

  if (isOpen) {
    dropdown.style.display = 'none';
    display?.classList.remove('active');
    wrapper?.classList.remove('open');
    if (arrow) arrow.style.transform = 'rotate(0deg)';
  } else {
    dropdown.style.display = 'block';
    display?.classList.add('active');
    wrapper?.classList.add('open');
    if (arrow) arrow.style.transform = 'rotate(180deg)';

    // Ensure customer list is visible immediately
    const listEl = document.getElementById('subscription-customer-list');
    const loadingEl = document.getElementById('subscription-customer-loading');

    // If customers already loaded, show list immediately
    if (subscriptionModalState.customers.length > 0 && listEl) {
      listEl.style.display = 'block';
      renderCustomerList(subscriptionModalState.customers); // Force Re-render
      if (loadingEl) loadingEl.style.display = 'none';
    } else {
      // If empty, force load
      loadEnhancedCustomers();
    }

    // Connect search input focus
    setTimeout(() => {
      const searchInput = document.getElementById('subscription-customer-search-input');
      if (searchInput) searchInput.focus();
    }, 100);
  }
};

window.closeSubscriptionCustomerDropdown = function () {
  const dropdown = document.getElementById('subscription-customer-dropdown');
  const display = document.getElementById('subscription-customer-display');
  const arrow = display?.querySelector('.customer-selected-arrow');

  if (dropdown) dropdown.style.display = 'none';
  if (display) display.classList.remove('active');
  if (arrow) arrow.style.transform = 'rotate(0deg)';
};

// Filter customers in the dropdown
window.filterSubscriptionCustomers = function (query) {
  const list = document.getElementById('subscription-customer-list');
  if (!list) return;

  const items = list.querySelectorAll('.dropdown-list-item');
  const term = query.toLowerCase();
  let visibleCount = 0;

  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    if (text.includes(term)) {
      item.style.display = 'flex';
      visibleCount++;
    } else {
      item.style.display = 'none';
    }
  });
};

// Select a customer from the list
window.selectEnhancedCustomer = function (customerId, customerName) {
  subscriptionModalState.selectedCustomerId = customerId;
  subscriptionModalState.selectedCustomerName = customerName;

  // Update hidden input
  document.getElementById('subscription-customer-id').value = customerId;

  // Update display text on the CARD
  const displayPlaceholder = document.getElementById('subscription-customer-placeholder');
  if (displayPlaceholder) {
    displayPlaceholder.textContent = customerName;
    displayPlaceholder.classList.add('selected-value');
    displayPlaceholder.style.color = 'var(--color-text)';
    displayPlaceholder.style.fontWeight = '500';
  }

  // Highlight selected item in list
  document.querySelectorAll('#subscription-customer-list .dropdown-list-item').forEach(item => {
    item.classList.remove('selected');
    if (item.dataset.id == customerId) item.classList.add('selected');
  });

  // Close dropdown
  closeSubscriptionCustomerDropdown();

  // Load suggestions
  loadSmartSuggestions(customerId);
  validateSubscriptionForm();
}

// Clear context
window.clearCustomerContext = function () {
  subscriptionModalState.contextMode = false;
  subscriptionModalState.selectedCustomerId = null;
  subscriptionModalState.selectedCustomerName = null;

  document.getElementById('subscription-customer-id').value = '';

  const displayPlaceholder = document.getElementById('subscription-customer-placeholder');
  if (displayPlaceholder) {
    displayPlaceholder.textContent = 'Select customer...';
    displayPlaceholder.style.color = '';
    displayPlaceholder.style.fontWeight = '';
    displayPlaceholder.classList.remove('selected-value');
  }

  // Clear search input too
  const searchInput = document.getElementById('subscription-customer-search-input');
  if (searchInput) searchInput.value = '';

  hideSmartSuggestions();
};

// Render the customer list
function renderCustomerList(customers) {
  const listEl = document.getElementById('subscription-customer-list');
  if (!listEl) return;

  listEl.innerHTML = '';

  customers.forEach(customer => {
    const item = document.createElement('div');
    item.className = 'dropdown-list-item';
    // Add data-id for easier selection tracking
    item.dataset.id = customer.id;

    // Check if selected
    if (customer.id == subscriptionModalState.selectedCustomerId) {
      item.classList.add('selected');
    }

    item.innerHTML = `
      <span class="trigger-icon">👤</span>
      <span>${customer.name}</span>
    `;

    item.onclick = (e) => {
      e.stopPropagation();
      selectEnhancedCustomer(customer.id, customer.name);
    };
    listEl.appendChild(item);
  });

  // "Create New" link
  const createLink = document.createElement('div');
  createLink.className = 'dropdown-list-item create-new-link';
  createLink.style.borderTop = '1px solid var(--color-border)';
  createLink.style.color = 'var(--color-primary)';
  createLink.innerHTML = '<span class="trigger-icon">+</span><span>Create New Customer</span>';
  createLink.onclick = () => window.location.href = '/customers?action=new';
  listEl.appendChild(createLink);
}

// Load customers (fetch)
window.loadEnhancedCustomers = function () {
  subscriptionModalState.loading = true;
  const loadingEl = document.getElementById('subscription-customer-loading');
  if (loadingEl) loadingEl.style.display = 'block';

  fetch('/api/customers')
    .then(r => r.json())
    .then(customers => {
      subscriptionModalState.customers = customers;
      subscriptionModalState.loading = false;
      if (loadingEl) loadingEl.style.display = 'none';
      renderCustomerList(customers);
    })
    .catch(e => {
      console.error("Error loading customers", e);
      if (loadingEl) loadingEl.textContent = "Error loading customers";
    });
};

// Preselect customer (for edit mode)
window.preselectCustomer = function (customerId, customerName) {
  selectEnhancedCustomer(customerId, customerName);
};

// Close dropdowns when clicking outside
document.addEventListener('click', function (e) {
  if (!e.target.closest('#subscription-customer-wrapper')) {
    closeSubscriptionCustomerDropdown();
  }
  if (!e.target.closest('#subscription-categories-wrapper')) {
    closeSubscriptionCategorySelector();
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
      tag.className = 'chip';
      tag.innerHTML = `
        <span>${cat.name}</span>
        <span class="chip-remove" onclick="event.stopPropagation(); removeCategoryChip(${cat.id})">×</span>
      `;
      display.appendChild(tag);
    });

    // Show "+X more" if there are more categories
    if (remainingCount > 0) {
      const moreTag = document.createElement('div');
      moreTag.className = 'chip';
      moreTag.style.background = 'var(--color-bg-secondary)';
      moreTag.style.color = 'var(--color-text-secondary)';
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
    .then(subscriptions => {
      const vendorSet = new Set(seededVendors); // Start with seeds
      subscriptions.forEach(sub => {
        if (sub.vendor_name) {
          vendorSet.add(sub.vendor_name);
        }
      });
      subscriptionModalState.vendors = Array.from(vendorSet).sort();
      console.log('Loaded vendors:', subscriptionModalState.vendors.length);
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
    minChars: 0, // Allow clicking to show all
    maxResults: 50, // Show more results
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
      // Don't clear interval, keep checking for updates
    }
  }, 1000);
}

// Filter Categories
window.filterSubscriptionCategories = function (query) {
  const list = document.querySelector('#subscription-categories-dropdown .categories-dropdown-list');
  if (!list) return;

  const items = list.querySelectorAll('.tags-dropdown-item');
  const term = query.toLowerCase();

  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    if (text.includes(term)) {
      item.style.display = 'flex';
    } else {
      item.style.display = 'none';
    }
  });
};

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

// ==================== VALIDATION LOGIC ====================

function validateSubscriptionForm() {
  const form = document.getElementById('subscription-form');
  const customerId = document.getElementById('subscription-customer-id').value;
  const vendorName = document.getElementById('subscription-vendor-name').value;
  const cost = document.querySelector('input[name="cost"]').value;
  const submitBtn = form.querySelector('button[type="submit"]');

  const isValid = customerId && vendorName && cost;

  // Toggle button state
  if (submitBtn) {
    submitBtn.disabled = !isValid;
    if (!isValid) {
      submitBtn.title = "Please fill in all required fields (Customer, Vendor, Cost)";
    } else {
      submitBtn.title = "";
    }
  }

  // Visual feedback for missing fields (on blur or change)
  if (!customerId) {
    const wrapper = document.getElementById('customer-selected-display');
    if (wrapper) wrapper.classList.add('invalid');
  } else {
    document.getElementById('customer-selected-display')?.classList.remove('invalid');
  }

  return isValid;
}

// Add validation listeners
document.addEventListener('DOMContentLoaded', () => {
  const inputs = ['subscription-vendor-name', 'subscription-customer-id'];
  const costInput = document.querySelector('input[name="cost"]');

  inputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', validateSubscriptionForm);
      el.addEventListener('change', validateSubscriptionForm);
    }
  });

  if (costInput) {
    costInput.addEventListener('input', validateSubscriptionForm);
  }

  // Also listen for customer selection changes via state
  // (This is handled in selectEnhancedCustomer)
});

// ==================== UNIFIED SUBMISSION HANDLER ====================

// Save subscription (Create or Update)
window.saveEnhancedSubscription = function (formData, itemId = null) {
  if (!validateSubscriptionForm()) {
    showToast('Please fill in all required fields.', 'error');
    return;
  }

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
      const customerName = subscriptionModalState.selectedCustomerName || formData.customer_name;
      showToast(`Success: ${formData.vendor_name} subscription ${action} for ${customerName || 'customer'}`, 'success');

      // Close modal
      const modal = document.getElementById('subscriptionModal');
      if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
          modal.style.display = 'none';
          document.body.classList.remove('modal-open');
          document.body.style.paddingRight = '';
        }, 300);
      }

      // Refresh the page to show new data
      // In a full SPA this would re-fetch just the table, but for now reload is safest
      setTimeout(() => window.location.reload(), 1000); // 1s delay to let user see toast
    })
    .catch(error => {
      console.error('Error saving subscription:', error);
      showToast(error.message || 'Error saving subscription', 'error');
    });
};
