// SubTrack Web - Enhanced Main JavaScript

// ==================== Theme Management ====================
function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  const savedVisualTheme = localStorage.getItem('visual-theme');
  
  // If visual theme is set, use that, otherwise use light/dark theme
  if (savedVisualTheme && savedVisualTheme !== 'default') {
    document.documentElement.setAttribute('data-theme', savedVisualTheme);
  } else {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
  updateThemeIcon(savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  
  // Check if currently on a visual theme
  const visualThemes = ['sunset', 'midnight', 'forest', 'candy', 'aurora'];
  const isVisualTheme = visualThemes.includes(currentTheme);
  
  let newTheme;
  if (isVisualTheme || currentTheme === 'light' || currentTheme === 'default') {
    newTheme = 'dark';
  } else {
    newTheme = 'light';
  }
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  localStorage.removeItem('visual-theme'); // Clear visual theme when toggling
  updateThemeIcon(newTheme);
  
  showToast(`Switched to ${newTheme} mode`, 'success');
}

function updateThemeIcon(theme) {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const isLight = (currentTheme === 'light' || currentTheme === 'default');

  const icon = document.getElementById('theme-icon');
  if (icon) {
    // Show moon for light themes, sun for dark themes
    icon.textContent = isLight ? '🌙' : '☀️';
  }

}

// ==================== Modal Management ====================
// Track open modals
window.openModals = window.openModals || [];

function openModal(modalId) {
  // Check if any modal is already open
  const openModalExists = window.openModals.length > 0;
  if (openModalExists) {
    showToast('Please close the current window first', 'warning');
    return;
  }
  
  const modal = document.getElementById(modalId);
  if (modal) {
    // Prevent page layout shift when locking scroll (scrollbar disappears)
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.body.classList.add('modal-open');
    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    }

    modal.style.display = 'block';

    // Track this modal
    window.openModals.push(modalId);
    
    // If opening customer modals, ensure group dropdown is populated
    if (modalId === 'customerModal' || modalId === 'editCustomerModal') {
      const categorySelect = modal.querySelector('select[name="category_id"]');
      const categoryId = categorySelect ? categorySelect.value : null;
      if (categoryId) {
        updateGroupSelect(categoryId, 'group_id');
      }
    }
    
    // If opening subscription modals, ensure customer dropdown is populated
    if (modalId === 'subscriptionModal' || modalId === 'editSubscriptionModal') {
      const categorySelect = modal.querySelector('select[name="category_id"]');
      const customerSelect = modal.querySelector('select[name="customer_id"]');
      const categoryId = categorySelect ? categorySelect.value : null;
      const selectedCustomerId = customerSelect ? customerSelect.value : null;
      updateCustomerSelect(categoryId, 'customer_id', selectedCustomerId);
    }

    // Animation
    requestAnimationFrame(() => {
      modal.classList.add('show');
    });
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('show');
    setTimeout(() => {
      modal.style.display = 'none';
      document.body.classList.remove('modal-open');
      document.body.style.paddingRight = '';
    }, 300);
    
    // Remove from tracking
    window.openModals = window.openModals.filter(id => id !== modalId);
  }
}

function closeAllModals() {
  document.querySelectorAll('.modal').forEach(modal => {
    modal.classList.remove('show');
    setTimeout(() => {
      modal.style.display = 'none';
    }, 300);
  });

  document.body.classList.remove('modal-open');
  document.body.style.paddingRight = '';

  // Clear tracking
  window.openModals = [];
}

// Close modal on backdrop click
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal')) {
    const rect = e.target.getBoundingClientRect();
    const clickedInside = (
      e.clientX >= rect.left &&
      e.clientX <= rect.right &&
      e.clientY >= rect.top &&
      e.clientY <= rect.bottom
    );
    
    // Check if clicked on backdrop (outside modal content)
    const modalContent = e.target.querySelector('.modal-content');
    if (modalContent && !modalContent.contains(e.target)) {
      closeAllModals();
    }
  }
});

// ==================== Keyboard Shortcuts ====================
document.addEventListener('keydown', function(e) {
  // Escape - Close modals
  if (e.key === 'Escape') {
    closeAllModals();
    const cmdPalette = document.getElementById('command-palette');
    if (cmdPalette && cmdPalette.style.display !== 'none') {
      closeCommandPalette();
    }
    return;
  }
  
  // Ignore if user is typing in an input
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
    return;
  }
  
  // / - Focus search
  if (e.key === '/') {
    e.preventDefault();
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
      searchInput.focus();
    }
  }
  
  // n - New item (open quick add)
  if (e.key === 'n' || e.key === 'N') {
    e.preventDefault();
    openModal('quickAddModal');
  }
  
  // Ctrl+K or Cmd+K - Command palette
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    openCommandPalette();
  }
  
  // b - Toggle sidebar
  if (e.key === 'b' || e.key === 'B') {
    e.preventDefault();
    toggleSidebarCollapse();
  }
});

// ==================== Visual Theme Switcher ====================
window.setVisualTheme = function(themeName) {
  document.documentElement.setAttribute('data-theme', themeName);
  localStorage.setItem('visual-theme', themeName);
  
  const themeNames = {
    'default': 'Ocean',
    'sunset': 'Sunset',
    'midnight': 'Midnight',
    'forest': 'Forest',
    'candy': 'Candy',
    'aurora': 'Aurora'
  };
  
  showToast(`Theme changed to ${themeNames[themeName]}`, 'success');
};

// ==================== Initialize ====================
document.addEventListener('DOMContentLoaded', function() {
  console.log('SubTrack Web Enhanced - Initialized');
  
  // Initialize theme first
  initTheme();
  
  // Configure HTMX
  if (typeof htmx !== 'undefined') {
    htmx.config.defaultSwapStyle = 'innerHTML';
    htmx.config.defaultSwapDelay = 200;
    htmx.config.defaultSettleDelay = 100;
    
    // HTMX event listeners
    document.body.addEventListener('htmx:afterSwap', function(evt) {
      // Re-initialize any components after HTMX swap
      refreshTooltips();
    });
    
    document.body.addEventListener('htmx:afterSettle', function(evt) {
      // Refresh tooltips after content settles
      refreshTooltips();
    });
  }
  
  // Initialize tooltips
  initTooltips();
  
  // Setup cascading selects
  document.querySelectorAll('select[name="category_id"]').forEach(select => {
    select.addEventListener('change', function() {
      // Find the modal this select is in to get the correct group_id select
      const modal = select.closest('.modal');
      const groupSelectId = modal ? 'group_id' : 'group_id';
      updateGroupSelect(this.value, groupSelectId);
      updateCustomerSelect(this.value);
    });
  });
  
  // Close search results when clicking outside
  document.addEventListener('click', function(e) {
    const searchWrapper = document.querySelector('.navbar-search');
    const searchResults = document.getElementById('search-results');
    
    if (searchWrapper && searchResults && !searchWrapper.contains(e.target)) {
      searchResults.innerHTML = '';
    }
  });
});

// Smooth scroll for anchor links
document.addEventListener('click', function(e) {
  if (e.target.tagName === 'A' && e.target.hash) {
    const target = document.querySelector(e.target.hash);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  }
});

// Toast notifications
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    padding: 16px 24px;
    background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
  `;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Debounce function for search
function debounce(func, wait) {
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

// Format currency
function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
}

// Calculate days until date
function daysUntil(dateString) {
  const date = new Date(dateString);
  const today = new Date();
  const diffTime = date - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}

// Confirmation dialog
function confirmAction(message, callback) {
  if (confirm(message)) {
    callback();
  }
}

// Link decision/unlink actions removed (AI/link automation disabled in this deployment)

// AI insights removed (AI features are not configured in this deployment)
window.refreshInsights = function() {
  showToast('Insights are disabled', 'info');
};

// Link analysis removed (AI features are not configured in this deployment)
window.runLinkAnalysis = function() {
  showToast('Link analysis is disabled', 'info');
};

// ==================== CRUD Operations ====================

// Load item data for editing
window.loadEditData = function(type, id) {
  // Handle irregular plurals (category -> categories)
  const pluralType = type === 'category' ? 'categories' : `${type}s`;
  fetch(`/api/${pluralType}/${id}`)
    .then(response => response.json())
    .then(data => {
      const modalId = `edit${type.charAt(0).toUpperCase() + type.slice(1)}Modal`;
      
      // Populate form fields
      const form = document.querySelector(`#${modalId} form`);
      Object.keys(data).forEach(key => {
        const field = form.querySelector(`[name="${key}"]`);
        if (field) {
          field.value = data[key] || '';
        }
      });
      
      // Store ID for update
      form.dataset.itemId = id;

      // Special handling: customer edit needs group dropdown populated based on category
      if (type === 'customer') {
        const categoryField = form.querySelector('select[name="category_id"]');
        const groupField = form.querySelector('select[name="group_id"]');
        const categoryId = categoryField ? categoryField.value : null;
        const groupId = groupField ? groupField.value : null;

        // Populate groups (filtered by category when present) and re-select current group.
        updateGroupSelect(categoryId, 'group_id');
        
        // If there's a group selected, set it after groups are loaded
        if (groupId) {
          // Small delay to ensure groups are loaded first
          setTimeout(() => {
            const groupSelect = form.querySelector('select[name="group_id"]');
            if (groupSelect) {
              groupSelect.value = groupId;
            }
          }, 100);
        }

        // Ensure future category changes keep group list in sync.
        if (categoryField && !categoryField.dataset.groupHooked) {
          categoryField.addEventListener('change', function() {
            updateGroupSelect(this.value, 'group_id');
          });
          categoryField.dataset.groupHooked = 'true';
        }
      }

      // Special handling: subscription edit needs customer dropdown populated based on category
      if (type === 'subscription') {
        const categoryField = form.querySelector('select[name="category_id"]');
        const customerField = form.querySelector('select[name="customer_id"]');
        const categoryId = categoryField ? categoryField.value : null;
        const customerId = customerField ? customerField.value : null;

        // Populate customers (filtered by category when present) and re-select current customer.
        updateCustomerSelect(categoryId, 'customer_id', customerId);

        // Ensure future category changes keep customer list in sync.
        if (categoryField && !categoryField.dataset.customerHooked) {
          categoryField.addEventListener('change', function() {
            updateCustomerSelect(this.value, 'customer_id');
          });
          categoryField.dataset.customerHooked = 'true';
        }
      }
      
      openModal(modalId);
    })
    .catch(error => {
      showToast('Error loading data', 'error');
      console.error('Error:', error);
    });
};

// Create Category
window.createCategory = function(formData) {
  fetch('/api/categories', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: formData.name,
      description: formData.description
    })
  })
  .then(response => response.json())
  .then(data => {
    showToast('Category created successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error creating category', 'error');
    console.error('Error:', error);
  });
};

// Open Group Modal with pre-selected category
window.openGroupModalForCategory = function(categoryId) {
  openModal('groupModal');
  // Pre-select the category after modal opens
  setTimeout(() => {
    const categorySelect = document.querySelector('#groupModal select[name="category_id"]');
    if (categorySelect) {
      categorySelect.value = categoryId;
    }
  }, 50);
};

// Open Customer Modal with pre-selected category
window.openCustomerModalForCategory = function(categoryId) {
  openModal('customerModal');
  // Pre-select the category and load groups for that category
  setTimeout(() => {
    const categorySelect = document.querySelector('#customerModal select[name="category_id"]');
    if (categorySelect) {
      categorySelect.value = categoryId;
      updateGroupSelect(categoryId, 'group_id');
    }
  }, 50);
};

// Create Group
window.createGroup = function(formData) {
  fetch('/api/groups', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: formData.name,
      category_id: parseInt(formData.category_id),
      notes: formData.notes
    })
  })
  .then(response => response.json())
  .then(data => {
    showToast('Group created successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error creating group', 'error');
    console.error('Error:', error);
  });
};

// Create Customer
window.createCustomer = function(formData) {
  fetch('/api/customers', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: formData.name,
      category_id: parseInt(formData.category_id),
      group_id: formData.group_id ? parseInt(formData.group_id) : null,
      email: formData.email || null,
      phone: formData.phone || null,
      tags: formData.tags || null,
      notes: formData.notes || null
    })
  })
  .then(response => response.json())
  .then(data => {
    showToast('Customer created successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error creating customer', 'error');
    console.error('Error:', error);
  });
};

// Create Subscription
window.createSubscription = function(formData) {
  fetch('/api/subscriptions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      vendor_name: formData.vendor_name,
      plan_name: formData.plan_name || null,
      cost: parseFloat(formData.cost),
      currency: formData.currency || 'USD',
      billing_cycle: formData.billing_cycle,
      start_date: formData.start_date,
      next_renewal_date: formData.next_renewal_date,
      status: formData.status || 'active',
      customer_id: parseInt(formData.customer_id),
      category_id: parseInt(formData.category_id),
      notes: formData.notes || null
    })
  })
  .then(response => response.json())
  .then(data => {
    showToast('Subscription created successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error creating subscription', 'error');
    console.error('Error:', error);
  });
};

// Update Category
window.updateCategory = function(formData, id) {
  fetch(`/api/categories/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: formData.name,
      description: formData.description
    })
  })
  .then(response => response.json())
  .then(data => {
    showToast('Category updated successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error updating category', 'error');
    console.error('Error:', error);
  });
};

// Update Group
window.updateGroup = function(formData, id) {
  fetch(`/api/groups/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: formData.name,
      category_id: parseInt(formData.category_id),
      notes: formData.notes
    })
  })
  .then(response => response.json())
  .then(data => {
    showToast('Group updated successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error updating group', 'error');
    console.error('Error:', error);
  });
};

// Update Customer
window.updateCustomer = function(formData, id) {
  fetch(`/api/customers/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: formData.name,
      category_id: parseInt(formData.category_id),
      group_id: formData.group_id ? parseInt(formData.group_id) : null,
      email: formData.email || null,
      phone: formData.phone || null,
      tags: formData.tags || null,
      notes: formData.notes || null
    })
  })
  .then(response => response.json())
  .then(data => {
    showToast('Customer updated successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error updating customer', 'error');
    console.error('Error:', error);
  });
};

// Update Subscription
window.updateSubscription = function(formData, id) {
  fetch(`/api/subscriptions/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      vendor_name: formData.vendor_name,
      plan_name: formData.plan_name || null,
      cost: parseFloat(formData.cost),
      currency: formData.currency || 'USD',
      billing_cycle: formData.billing_cycle,
      start_date: formData.start_date,
      next_renewal_date: formData.next_renewal_date,
      status: formData.status || 'active',
      customer_id: parseInt(formData.customer_id),
      category_id: parseInt(formData.category_id),
      notes: formData.notes || null
    })
  })
  .then(response => response.json())
  .then(data => {
    showToast('Subscription updated successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error updating subscription', 'error');
    console.error('Error:', error);
  });
};

// Delete with confirmation and undo option
window.deleteItem = function(type, id, name) {
  const confirmMsg = `Delete "${name}"?\n\nThis will remove:\n• The ${type} itself\n• All associated data\n\nThis action can be undone for 10 seconds.`;
  
  if (!confirm(confirmMsg)) {
    return;
  }
  
  const endpoints = {
    category: '/api/categories',
    group: '/api/groups',
    customer: '/api/customers',
    subscription: '/api/subscriptions'
  };
  
  // Store delete info for potential undo
  let undoTimeout;
  let deleteExecuted = false;
  
  // Show undo toast
  const undoToast = document.createElement('div');
  undoToast.className = 'toast toast-warning';
  undoToast.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    padding: 16px 24px;
    background: #f59e0b;
    color: white;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
    display: flex;
    align-items: center;
    gap: 12px;
  `;
  undoToast.innerHTML = `
    <span>Deleting "${name}"...</span>
    <button onclick="window.cancelDelete()" style="background: white; color: #f59e0b; border: none; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-weight: bold;">UNDO</button>
  `;
  
  document.body.appendChild(undoToast);
  
  // Store cancel function globally
  window.cancelDelete = function() {
    clearTimeout(undoTimeout);
    undoToast.remove();
    if (!deleteExecuted) {
      showToast('Delete cancelled', 'info');
    }
  };
  
  // Execute delete after 10 seconds
  undoTimeout = setTimeout(() => {
    deleteExecuted = true;
    undoToast.remove();
    
    fetch(`${endpoints[type]}/${id}`, {
      method: 'DELETE'
    })
    .then(response => {
      if (response.ok) {
        showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} deleted successfully`, 'success');
        setTimeout(() => window.location.reload(), 500);
      } else {
        throw new Error('Delete failed');
      }
    })
    .catch(error => {
      showToast(`Error deleting ${type}`, 'error');
      console.error('Error:', error);
    });
  }, 10000);
};

// ==================== Tooltips ====================
function initTooltips() {
  // Modern tooltips use CSS ::before/::after pseudo-elements via data attributes
  // No JavaScript initialization needed for [data-tooltip] elements
  
  // Legacy tooltip support for dynamically added elements
  const legacyTooltips = document.querySelectorAll('.tooltip:not([data-tooltip])');
  legacyTooltips.forEach(el => {
    if (!el.querySelector('.tooltip-text') && el.title) {
      const tooltipText = document.createElement('span');
      tooltipText.className = 'tooltip-text';
      tooltipText.textContent = el.title;
      el.appendChild(tooltipText);
      el.removeAttribute('title');
    }
  });
}

// Dynamic tooltip refresh for HTMX swapped content
function refreshTooltips() {
  initTooltips();
}

// ==================== Form Helpers ====================
window.handleFormSubmit = function(event, callback) {
  event.preventDefault();
  const formData = new FormData(event.target);
  const data = Object.fromEntries(formData.entries());
  
  // Check if this is an edit operation
  const itemId = event.target.dataset.itemId;
  if (itemId) {
    callback(data, itemId);
  } else {
    callback(data);
  }
};

// Dynamic cascading selects
window.updateGroupSelect = function(categoryId, groupSelectId = 'group_id') {
  // Find the group select - prefer searching within open modals first
  let groupSelect = null;
  
  // Try to find within an open modal
  const openModals = document.querySelectorAll('.modal[style*="display: block"]');
  for (let modal of openModals) {
    const select = modal.querySelector(`select[name="${groupSelectId}"]`);
    if (select) {
      groupSelect = select;
      break;
    }
  }
  
  // Fallback to global search if not found in modals
  if (!groupSelect) {
    groupSelect = document.querySelector(`select[name="${groupSelectId}"]`);
  }
  
  if (!groupSelect) return;
  
  if (!categoryId) {
    groupSelect.innerHTML = '<option value="">No group</option>';
    return;
  }
  
  fetch(`/api/groups?category_id=${categoryId}`)
    .then(response => response.json())
    .then(groups => {
      groupSelect.innerHTML = '<option value="">No group</option>';
      groups.forEach(group => {
        const option = document.createElement('option');
        option.value = group.id;
        option.textContent = group.name;
        groupSelect.appendChild(option);
      });
    })
    .catch(error => console.error('Error loading groups:', error));
};

window.updateCustomerSelect = function(categoryId, customerSelectId = 'customer_id', selectedCustomerId = null) {
  const customerSelect = document.querySelector(`select[name="${customerSelectId}"]`);
  if (!customerSelect) return;

  // If no category selected, still load all customers so the dropdown isn't empty.
  const url = categoryId ? `/api/customers?category_id=${categoryId}` : `/api/customers`;

  fetch(url)
    .then(response => response.json())
    .then(customers => {
      customerSelect.innerHTML = '<option value="">Select a customer</option>';
      customers.forEach(customer => {
        const option = document.createElement('option');
        option.value = customer.id;
        option.textContent = customer.name;
        if (selectedCustomerId && String(customer.id) === String(selectedCustomerId)) {
          option.selected = true;
        }
        customerSelect.appendChild(option);
      });
    })
    .catch(error => {
      console.error('Error loading customers:', error);
      customerSelect.innerHTML = '<option value="">Select a customer</option>';
    });
};

// ==================== Sidebar Toggle ====================
window.toggleSidebar = function() {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.classList.toggle('open');
  }
};

window.toggleSidebarCollapse = function() {
  document.body.classList.toggle('sidebar-collapsed');
  const isCollapsed = document.body.classList.contains('sidebar-collapsed');
  localStorage.setItem('sidebar-collapsed', isCollapsed);
  showToast(isCollapsed ? 'Sidebar collapsed' : 'Sidebar expanded', 'info');
};

// Load sidebar state on page load
if (localStorage.getItem('sidebar-collapsed') === 'true') {
  document.body.classList.add('sidebar-collapsed');
}

// ==================== Command Palette ====================
window.openCommandPalette = function() {
  let palette = document.getElementById('command-palette');
  
  if (!palette) {
    // Create command palette
    palette = document.createElement('div');
    palette.id = 'command-palette';
    palette.className = 'command-palette';
    palette.innerHTML = `
      <div class="command-palette-backdrop" onclick="closeCommandPalette()"></div>
      <div class="command-palette-container">
        <input type="text" id="command-search" class="command-search" placeholder="Type a command or search..." autofocus>
        <div id="command-results" class="command-results"></div>
      </div>
    `;
    document.body.appendChild(palette);
    
    const searchInput = document.getElementById('command-search');
    searchInput.addEventListener('input', handleCommandSearch);
    searchInput.addEventListener('keydown', handleCommandNavigation);
  }
  
  palette.style.display = 'block';
  document.getElementById('command-search').value = '';
  document.getElementById('command-search').focus();
  showDefaultCommands();
};

window.closeCommandPalette = function() {
  const palette = document.getElementById('command-palette');
  if (palette) {
    palette.style.display = 'none';
  }
};

function showDefaultCommands() {
  const commands = [
    { icon: '➕', name: 'New Subscription', action: () => { closeCommandPalette(); openModal('subscriptionModal'); } },
    { icon: '👤', name: 'New Customer', action: () => { closeCommandPalette(); openModal('customerModal'); } },
    { icon: '📁', name: 'New Category', action: () => { closeCommandPalette(); openModal('categoryModal'); } },
    { icon: '📦', name: 'New Group', action: () => { closeCommandPalette(); openModal('groupModal'); } },
    { icon: '📊', name: 'Go to Dashboard', action: () => { closeCommandPalette(); window.location.href = '/'; } },
    { icon: '📁', name: 'Go to Categories', action: () => { closeCommandPalette(); window.location.href = '/categories'; } },
    { icon: '🔗', name: 'Go to Links', action: () => { closeCommandPalette(); window.location.href = '/links'; } },
    { icon: '⚙️', name: 'Go to Settings', action: () => { closeCommandPalette(); window.location.href = '/settings'; } },
    { icon: '🌙', name: 'Toggle Theme', action: () => { closeCommandPalette(); toggleTheme(); } },
    { icon: '🤖', name: 'Run Link Analysis', action: () => { closeCommandPalette(); analyzeLinks(); } },
  ];
  
  displayCommands(commands);
}

function handleCommandSearch(e) {
  const query = e.target.value.toLowerCase();
  
  if (!query) {
    showDefaultCommands();
    return;
  }
  
  const allCommands = [
    { icon: '➕', name: 'New Subscription', action: () => { closeCommandPalette(); openModal('subscriptionModal'); } },
    { icon: '👤', name: 'New Customer', action: () => { closeCommandPalette(); openModal('customerModal'); } },
    { icon: '📁', name: 'New Category', action: () => { closeCommandPalette(); openModal('categoryModal'); } },
    { icon: '📦', name: 'New Group', action: () => { closeCommandPalette(); openModal('groupModal'); } },
    { icon: '📊', name: 'Dashboard', action: () => { closeCommandPalette(); window.location.href = '/'; } },
    { icon: '📁', name: 'Categories', action: () => { closeCommandPalette(); window.location.href = '/categories'; } },
    { icon: '🔗', name: 'Links', action: () => { closeCommandPalette(); window.location.href = '/links'; } },
    { icon: '⚙️', name: 'Settings', action: () => { closeCommandPalette(); window.location.href = '/settings'; } },
    { icon: '🌙', name: 'Toggle Theme', action: () => { closeCommandPalette(); toggleTheme(); } },
    { icon: '🤖', name: 'Run Link Analysis', action: () => { closeCommandPalette(); analyzeLinks(); } },
  ];
  
  const filtered = allCommands.filter(cmd => 
    cmd.name.toLowerCase().includes(query)
  );
  
  displayCommands(filtered);
}

function displayCommands(commands) {
  const results = document.getElementById('command-results');
  
  if (commands.length === 0) {
    results.innerHTML = '<div class="command-empty">No commands found</div>';
    return;
  }
  
  results.innerHTML = commands.map((cmd, index) => `
    <div class="command-item ${index === 0 ? 'selected' : ''}" data-index="${index}">
      <span class="command-icon">${cmd.icon}</span>
      <span class="command-name">${cmd.name}</span>
    </div>
  `).join('');
  
  // Add click handlers
  results.querySelectorAll('.command-item').forEach((item, index) => {
    item.addEventListener('click', () => {
      commands[index].action();
    });
  });
}

function handleCommandNavigation(e) {
  const results = document.getElementById('command-results');
  const items = results.querySelectorAll('.command-item');
  const selected = results.querySelector('.command-item.selected');
  let currentIndex = selected ? parseInt(selected.dataset.index) : 0;
  
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    currentIndex = (currentIndex + 1) % items.length;
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    currentIndex = (currentIndex - 1 + items.length) % items.length;
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (selected) {
      selected.click();
    }
    return;
  } else {
    return;
  }
  
  items.forEach((item, index) => {
    item.classList.toggle('selected', index === currentIndex);
  });
  
  items[currentIndex].scrollIntoView({ block: 'nearest' });
}

// ==================== Subscription Actions ====================
let renewalSubscriptionId = null;
let renewalSubscriptionData = null;

window.renewSubscription = function(subscriptionId) {
  // Store the subscription ID for the modal
  renewalSubscriptionId = subscriptionId;
  
  // Fetch subscription data
  fetch(`/api/subscriptions/${subscriptionId}`)
    .then(response => response.json())
    .then(subscription => {
      renewalSubscriptionData = subscription;
      
      // Show the renewal modal with options
      const modal = document.getElementById('renewalModal');
      if (!modal) {
        createRenewalModal();
      }
      
      // Set the billing cycle info
      const billingCycleText = subscription.billing_cycle.charAt(0).toUpperCase() + subscription.billing_cycle.slice(1);
      document.getElementById('renewal-billing-cycle').textContent = billingCycleText;
      document.getElementById('renewal-periods').value = '1';
      
      openModal('renewalModal');
    })
    .catch(error => {
      showToast('Error loading subscription', 'error');
      console.error('Error:', error);
    });
};

function createRenewalModal() {
  const modal = document.createElement('div');
  modal.id = 'renewalModal';
  modal.className = 'modal';
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h2 class="modal-title">🔄 Renew Subscription</h2>
        <button class="modal-close" onclick="closeModal('renewalModal')">×</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Billing Cycle</label>
          <div style="font-size: 18px; font-weight: 600; padding: 12px; background: var(--color-bg-secondary); border-radius: 8px;">
            <span id="renewal-billing-cycle">Monthly</span>
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">How many periods to renew?</label>
          <input type="number" id="renewal-periods" class="form-input" min="1" max="120" value="1" placeholder="1">
          <small class="text-secondary" style="display: block; margin-top: 8px;">
            You can renew for 1 or more billing cycles at once
          </small>
        </div>
        
        <div style="background: var(--color-bg-secondary); padding: 12px; border-radius: 8px; margin-top: 16px;">
          <div style="font-size: 13px; color: var(--color-text-secondary); margin-bottom: 8px;">Preview:</div>
          <div style="font-size: 16px; font-weight: 600;">
            New renewal date: <span id="renewal-date-preview">-</span>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" onclick="closeModal('renewalModal')">Cancel</button>
        <button type="button" class="btn btn-primary" onclick="confirmRenewal()">Renew Subscription</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  
  // Add event listener to update preview
  document.getElementById('renewal-periods').addEventListener('input', updateRenewalPreview);
}

function updateRenewalPreview() {
  if (!renewalSubscriptionData) return;
  
  const periods = parseInt(document.getElementById('renewal-periods').value) || 1;
  const currentDate = new Date(renewalSubscriptionData.next_renewal_date);
  let newDate = new Date(currentDate);
  
  const billingCycle = renewalSubscriptionData.billing_cycle.toLowerCase();
  
  switch(billingCycle) {
    case 'monthly':
      newDate.setMonth(newDate.getMonth() + periods);
      break;
    case 'yearly':
      newDate.setFullYear(newDate.getFullYear() + periods);
      break;
    case 'quarterly':
      newDate.setMonth(newDate.getMonth() + (3 * periods));
      break;
    case 'weekly':
      newDate.setDate(newDate.getDate() + (7 * periods));
      break;
  }
  
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  const formattedDate = newDate.toLocaleDateString('en-US', options);
  document.getElementById('renewal-date-preview').textContent = formattedDate;
}

window.confirmRenewal = function() {
  if (!renewalSubscriptionId || !renewalSubscriptionData) {
    showToast('Error: No subscription data', 'error');
    return;
  }
  
  const periods = parseInt(document.getElementById('renewal-periods').value) || 1;
  
  if (periods < 1) {
    showToast('Please enter at least 1 period', 'warning');
    return;
  }
  
  if (periods > 120) {
    showToast('Maximum 120 periods allowed', 'warning');
    return;
  }
  
  // Calculate new renewal date
  const currentDate = new Date(renewalSubscriptionData.next_renewal_date);
  let newDate = new Date(currentDate);
  
  const billingCycle = renewalSubscriptionData.billing_cycle.toLowerCase();
  
  switch(billingCycle) {
    case 'monthly':
      newDate.setMonth(newDate.getMonth() + periods);
      break;
    case 'yearly':
      newDate.setFullYear(newDate.getFullYear() + periods);
      break;
    case 'quarterly':
      newDate.setMonth(newDate.getMonth() + (3 * periods));
      break;
    case 'weekly':
      newDate.setDate(newDate.getDate() + (7 * periods));
      break;
  }
  
  // Update subscription
  fetch(`/api/subscriptions/${renewalSubscriptionId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...renewalSubscriptionData,
      next_renewal_date: newDate.toISOString().split('T')[0],
      status: 'active'
    })
  })
  .then(response => response.json())
  .then(data => {
    closeModal('renewalModal');
    showToast(`Subscription renewed for ${periods} ${renewalSubscriptionData.billing_cycle}(s)!`, 'success');
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error renewing subscription', 'error');
    console.error('Error:', error);
  });
};

window.pauseSubscription = function(subscriptionId) {
  if (!confirm('Pause this subscription? You can reactivate it later.')) {
    return;
  }
  
  fetch(`/api/subscriptions/${subscriptionId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      status: 'paused'
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to pause subscription');
    }
    return response.json();
  })
  .then(data => {
    showToast('Subscription paused', 'success');
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error pausing subscription', 'error');
    console.error('Error:', error);
  });
};

window.cancelSubscription = function(subscriptionId) {
  if (!confirm('Cancel this subscription? This will set the status to cancelled.')) {
    return;
  }
  
  fetch(`/api/subscriptions/${subscriptionId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      status: 'cancelled'
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to cancel subscription');
    }
    return response.json();
  })
  .then(data => {
    showToast('Subscription cancelled', 'success');
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    showToast('Error cancelling subscription', 'error');
    console.error('Error:', error);
  });
};

// ==================== AI Functions ====================
window.analyzeLinks = async function() {
  showToast('Analyzing links...', 'info');
  
  try {
    const response = await fetch('/api/ai/analyze-links', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ use_ai: false })
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze links');
    }
    
    const data = await response.json();
    showToast(`Found ${data.links_found} potential links!`, 'success');
    setTimeout(() => window.location.reload(), 1000);
  } catch (error) {
    showToast('Error analyzing links', 'error');
    console.error('Error:', error);
  }
};

window.acceptLink = async function(linkId) {
  try {
    const response = await fetch(`/api/ai/links/${linkId}/decide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision: 'accepted' })
    });
    
    if (!response.ok) {
      throw new Error('Failed to accept link');
    }
    
    showToast('Link accepted', 'success');
    setTimeout(() => window.location.reload(), 500);
  } catch (error) {
    showToast('Error accepting link', 'error');
    console.error('Error:', error);
  }
};

window.rejectLink = async function(linkId) {
  try {
    const response = await fetch(`/api/ai/links/${linkId}/decide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision: 'rejected' })
    });
    
    if (!response.ok) {
      throw new Error('Failed to reject link');
    }
    
    showToast('Link rejected', 'success');
    setTimeout(() => window.location.reload(), 500);
  } catch (error) {
    showToast('Error rejecting link', 'error');
    console.error('Error:', error);
  }
};

window.unlinkRelationship = async function(linkId) {
  if (!confirm('Remove this link permanently?')) {
    return;
  }
  
  try {
    const response = await fetch(`/api/ai/links/${linkId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error('Failed to unlink');
    }
    
    showToast('Link removed', 'success');
    setTimeout(() => window.location.reload(), 500);
  } catch (error) {
    showToast('Error removing link', 'error');
    console.error('Error:', error);
  }
};

window.saveAIConfig = function() {
  const apiKey = document.getElementById('ai-api-key').value;
  const model = document.getElementById('ai-model').value;
  const enabled = document.getElementById('ai-enabled').checked;
  
  localStorage.setItem('ai-api-key', apiKey);
  localStorage.setItem('ai-model', model);
  localStorage.setItem('ai-enabled', enabled);
  
  showToast('AI configuration saved', 'success');
  closeModal('aiConfigModal');
};

// Load AI config when modal opens
window.loadAIConfig = function() {
  const apiKey = localStorage.getItem('ai-api-key') || '';
  const model = localStorage.getItem('ai-model') || 'gemini-pro';
  const enabled = localStorage.getItem('ai-enabled') === 'true';
  
  const apiKeyInput = document.getElementById('ai-api-key');
  const modelSelect = document.getElementById('ai-model');
  const enabledCheckbox = document.getElementById('ai-enabled');
  
  if (apiKeyInput) apiKeyInput.value = apiKey;
  if (modelSelect) modelSelect.value = model;
  if (enabledCheckbox) enabledCheckbox.checked = enabled;
};

// ==================== Export Functions ====================
window.openShortcutsModal = function() {
  openModal('shortcutsModal');
};

window.openAboutModal = function() {
  openModal('aboutModal');
};

window.SubTrack = {
  toggleTheme,
  openModal,
  closeModal,
  closeAllModals,
  createCategory,
  createGroup,
  createCustomer,
  createSubscription,
  deleteItem,
  showToast,
  toggleSidebar,
  toggleSidebarCollapse,
  renewSubscription,
  pauseSubscription,
  cancelSubscription,
  openShortcutsModal,
  openAboutModal,
  analyzeLinks,
  acceptLink,
  rejectLink,
  unlinkRelationship,
  saveAIConfig,
  loadAIConfig
};
