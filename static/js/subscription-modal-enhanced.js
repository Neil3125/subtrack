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
window.initEnhancedSubscriptionModal = function(customerId = null, customerName = null, categoryId = null) {
  console.log('Initializing enhanced subscription modal', { customerId, customerName, categoryId });
  
  // Reset form
  document.getElementById('subscription-form').reset();
  
  // Set context mode if customer provided
  if (customerId && customerName) {
    subscriptionModalState.contextMode = true;
    subscriptionModalState.selectedCustomerId = customerId;
    subscriptionModalState.selectedCustomerName = customerName;
    
    // Show context alert
    showCustomerContext(customerName);
    
    // Pre-select customer
    preselectCustomer(customerId, customerName);
    
    // Load suggestions
    loadSmartSuggestions(customerId);
    
    // Pre-select category if provided
    if (categoryId) {
      setTimeout(() => {
        selectCategoryTag(categoryId);
      }, 100);
    }
  } else {
    subscriptionModalState.contextMode = false;
    hideCustomerContext();
  }
  
  // Load customers
  loadEnhancedCustomers();
  
  // Load vendors for autocomplete
  loadVendors();
  
  // Initialize vendor autocomplete
  initVendorAutocomplete();
};

// ==================== CUSTOMER CONTEXT ALERT ====================

function showCustomerContext(customerName) {
  const alert = document.getElementById('customer-context-alert');
  const nameSpan = document.getElementById('context-customer-name');
  
  if (alert && nameSpan) {
    nameSpan.textContent = customerName;
    alert.style.display = 'block';
  }
}

function hideCustomerContext() {
  const alert = document.getElementById('customer-context-alert');
  if (alert) {
    alert.style.display = 'none';
  }
}

window.clearCustomerContext = function() {
  subscriptionModalState.contextMode = false;
  subscriptionModalState.selectedCustomerId = null;
  subscriptionModalState.selectedCustomerName = null;
  
  hideCustomerContext();
  hideSmartSuggestions();
  
  // Reset customer dropdown
  const trigger = document.getElementById('subscription-customer-trigger');
  if (trigger) {
    const textEl = trigger.querySelector('.trigger-text');
    if (textEl) {
      textEl.textContent = 'Select a customer...';
      textEl.classList.add('placeholder');
    }
  }
  
  document.getElementById('subscription-customer-id').value = '';
};

// ==================== ENHANCED CUSTOMER DROPDOWN ====================

function loadEnhancedCustomers() {
  subscriptionModalState.loading = true;
  
  const loadingEl = document.getElementById('subscription-customer-loading');
  const listEl = document.getElementById('subscription-customer-list');
  const emptyEl = document.getElementById('subscription-customer-empty');
  const statusText = document.getElementById('customer-status-text');
  
  // Show loading
  if (loadingEl) loadingEl.style.display = 'block';
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
        if (emptyEl) emptyEl.style.display = 'block';
        if (statusText) statusText.textContent = 'No customers available';
      } else {
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
        emptyEl.innerHTML = '<span class="empty-icon">⚠️</span><span>Error loading customers</span>';
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

window.toggleEnhancedDropdown = function(prefix) {
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
  
  // Update trigger display
  const trigger = document.getElementById('subscription-customer-trigger');
  if (trigger) {
    const textEl = trigger.querySelector('.trigger-text');
    if (textEl) {
      textEl.textContent = customerName;
      textEl.classList.remove('placeholder');
    }
  }
  
  // Update list selection
  document.querySelectorAll('#subscription-customer-list .dropdown-list-item').forEach(item => {
    item.classList.remove('selected');
  });
  event.target.closest('.dropdown-list-item')?.classList.add('selected');
  
  // Close dropdown
  toggleEnhancedDropdown('subscription-customer');
  
  // Load suggestions
  loadSmartSuggestions(customerId);
}

window.filterEnhancedDropdown = function(prefix, searchText) {
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
document.addEventListener('click', function(e) {
  if (!e.target.closest('.enhanced-dropdown')) {
    document.querySelectorAll('.enhanced-dropdown-panel').forEach(panel => {
      panel.style.display = 'none';
    });
    document.querySelectorAll('.enhanced-dropdown-trigger').forEach(trigger => {
      trigger.classList.remove('open');
    });
  }
});

// ==================== SMART SUGGESTIONS ====================

function loadSmartSuggestions(customerId) {
  const panel = document.getElementById('smart-suggestions');
  const content = document.getElementById('suggestions-content');
  
  if (!panel || !content) return;
  
  fetch(`/api/subscriptions?customer_id=${customerId}`)
    .then(response => response.json())
    .then(subscriptions => {
      if (!subscriptions || subscriptions.length === 0) {
        panel.style.display = 'none';
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
        html += '<div style="margin-bottom: var(--space-2);"><strong style="font-size: var(--font-size-xs); color: var(--color-text-secondary);">📁 Frequently used categories:</strong></div>';
        html += '<div style="display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-3);">';
        categoryIds.forEach(catId => {
          html += `<div class="suggestion-chip" onclick="applySuggestion('category', ${catId}, '${categories[catId]}')">
            <span class="suggestion-chip-icon">📁</span>
            <span class="suggestion-chip-label">${categories[catId]}</span>
            <span class="suggestion-chip-action">+ Add</span>
          </div>`;
        });
        html += '</div>';
      }
      
      // Vendor suggestions
      const sortedVendors = Object.entries(vendors).sort((a, b) => b[1] - a[1]).slice(0, 5);
      if (sortedVendors.length > 0) {
        html += '<div style="margin-bottom: var(--space-2);"><strong style="font-size: var(--font-size-xs); color: var(--color-text-secondary);">🏢 Frequently used vendors:</strong></div>';
        html += '<div style="display: flex; flex-wrap: wrap; gap: var(--space-2);">';
        sortedVendors.forEach(([vendor, count]) => {
          const escapedVendor = vendor.replace(/'/g, "\\'");
          html += `<div class="suggestion-chip" onclick="applySuggestion('vendor', null, '${escapedVendor}')">
            <span class="suggestion-chip-icon">🏢</span>
            <span class="suggestion-chip-label">${vendor} <span style="color: var(--color-text-tertiary); font-size: var(--font-size-xs);">(${count}×)</span></span>
            <span class="suggestion-chip-action">+ Use</span>
          </div>`;
        });
        html += '</div>';
      }
      
      if (html) {
        content.innerHTML = html;
        panel.style.display = 'block';
      } else {
        panel.style.display = 'none';
      }
    })
    .catch(error => {
      console.error('Error loading suggestions:', error);
      panel.style.display = 'none';
    });
}

function hideSmartSuggestions() {
  const panel = document.getElementById('smart-suggestions');
  if (panel) {
    panel.style.display = 'none';
  }
}

window.applySuggestion = function(type, id, value) {
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

window.openCategorySelector = function() {
  const dropdown = document.getElementById('subscription-categories-dropdown');
  const display = document.getElementById('subscription-categories-tags');
  
  if (dropdown) {
    dropdown.style.display = 'block';
    display?.classList.add('active');
  }
};

window.closeCategorySelector = function() {
  const dropdown = document.getElementById('subscription-categories-dropdown');
  const display = document.getElementById('subscription-categories-tags');
  
  if (dropdown) {
    dropdown.style.display = 'none';
    display?.classList.remove('active');
  }
};

window.toggleCategoryTag = function(element) {
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
};

function selectCategoryTag(categoryId) {
  const item = document.querySelector(`.tags-dropdown-item[data-id="${categoryId}"]`);
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

window.removeCategoryChip = function(categoryId) {
  const item = document.querySelector(`.tags-dropdown-item[data-id="${categoryId}"]`);
  if (item) {
    item.classList.remove('selected');
  }
  removeCategoryFromSelection(categoryId);
};

function updateCategoryDisplay() {
  const display = document.getElementById('subscription-categories-tags');
  const idsInput = document.getElementById('subscription-category-ids');
  const idInput = document.getElementById('subscription-category-id');
  
  if (!display) return;
  
  display.innerHTML = '';
  
  if (subscriptionModalState.selectedCategories.length === 0) {
    display.innerHTML = '<span class="tags-placeholder">Click to select categories...</span>';
    idsInput.value = '';
    idInput.value = '';
  } else {
    subscriptionModalState.selectedCategories.forEach(cat => {
      const tag = document.createElement('div');
      tag.className = 'category-tag';
      tag.innerHTML = `
        <span class="category-tag-icon">📁</span>
        <span>${cat.name}</span>
        <span class="category-tag-remove" onclick="event.stopPropagation(); removeCategoryChip(${cat.id})">×</span>
      `;
      display.appendChild(tag);
    });
    
    // Update hidden inputs
    const ids = subscriptionModalState.selectedCategories.map(cat => cat.id);
    idsInput.value = ids.join(',');
    idInput.value = ids[0] || ''; // First category for backward compatibility
  }
}

// ==================== VENDOR AUTOCOMPLETE ====================

function loadVendors() {
  // Fetch unique vendors from subscriptions
  fetch('/api/subscriptions')
    .then(response => response.json())
    .then(subscriptions => {
      const vendorSet = new Set();
      subscriptions.forEach(sub => {
        if (sub.vendor_name) {
          vendorSet.add(sub.vendor_name);
        }
      });
      subscriptionModalState.vendors = Array.from(vendorSet).sort();
    })
    .catch(error => {
      console.error('Error loading vendors:', error);
      subscriptionModalState.vendors = [];
    });
}

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
window.openModal = function(modalId) {
  if (modalId === 'subscriptionModal') {
    initEnhancedSubscriptionModal();
  }
  originalOpenModal(modalId);
};

// Update the openSubscriptionModalForCustomer function
window.openSubscriptionModalForCustomer = function(categoryId, customerId, customerName) {
  // Open modal first
  originalOpenModal('subscriptionModal');
  
  // Then initialize with customer context
  setTimeout(() => {
    initEnhancedSubscriptionModal(customerId, customerName, categoryId);
  }, 100);
};

console.log('✅ Enhanced Subscription Modal loaded successfully');
