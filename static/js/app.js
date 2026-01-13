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
  
  // Clear search input to prevent autofill issues
  const searchInput = document.getElementById('global-search-input');
  if (searchInput && searchInput.value === 'admin') {
    searchInput.value = '';
  }
  
  const modal = document.getElementById(modalId);
  if (modal) {
    // Prevent page layout shift when locking scroll (scrollbar disappears)
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.body.classList.add('modal-open');
    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    }

    // Use grid display for proper centering and scrollable modal body
    modal.style.display = 'grid';

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
    // Sidebar collapse removed
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
  
  // Initialize country autocomplete
  initCountryAutocomplete();
  
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

// ==================== Smart Autocomplete System ====================
let cachedCountries = [];
const defaultCountries = [
  // A
  'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda',
  'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan',
  // B
  'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize',
  'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bonaire', 'Bosnia and Herzegovina',
  'Botswana', 'Brazil', 'British Virgin Islands', 'Brunei', 'Bulgaria', 'Burkina Faso',
  // C
  'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Republic',
  'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica', 'Croatia',
  'Cuba', 'Curaçao', 'Curacao', 'Cyprus', 'Czech Republic',
  // D
  'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic',
  // E
  'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia',
  // F
  'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia',
  // G
  'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland',
  'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guyana',
  // H
  'Haiti', 'Honduras', 'Hong Kong', 'Hungary',
  // I
  'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Isle of Man', 'Israel', 'Italy', 'Ivory Coast',
  // J
  'Jamaica', 'Japan', 'Jersey', 'Jordan',
  // K
  'Kazakhstan', 'Kenya', 'Kiribati', 'Kosovo', 'Kuwait', 'Kyrgyzstan',
  // L
  'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein',
  'Lithuania', 'Luxembourg',
  // M
  'Macau', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta',
  'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia',
  'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar',
  // N
  'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand',
  'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway',
  // O
  'Oman',
  // P
  'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay',
  'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico',
  // Q
  'Qatar',
  // R
  'Romania', 'Russia', 'Rwanda',
  // S
  'Saint Kitts and Nevis', 'Saint Lucia', 'St. Lucia', 'Saint Martin', 'Saint Vincent and the Grenadines',
  'Samoa', 'San Marino', 'São Tomé and Príncipe', 'Saudi Arabia', 'Senegal', 'Serbia',
  'Seychelles', 'Sierra Leone', 'Singapore', 'Sint Maarten', 'Slovakia', 'Slovenia',
  'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'South Sudan', 'Spain',
  'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria',
  // T
  'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga',
  'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu',
  // U
  'Uganda', 'Ukraine', 'United Arab Emirates', 'UAE', 'United Kingdom', 'UK', 'England',
  'Scotland', 'Wales', 'Northern Ireland', 'United States', 'USA', 'Uruguay', 'US Virgin Islands', 'Uzbekistan',
  // V
  'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam',
  // Y
  'Yemen',
  // Z
  'Zambia', 'Zimbabwe'
];

// Smart Autocomplete Class
class SmartAutocomplete {
  constructor(input, options = {}) {
    this.input = input;
    this.options = {
      minChars: options.minChars || 1,
      maxResults: options.maxResults || 8,
      highlightMatches: options.highlightMatches !== false,
      showRecentFirst: options.showRecentFirst !== false,
      dataSource: options.dataSource || [],
      placeholder: options.placeholder || 'Type to search...',
      emptyMessage: options.emptyMessage || 'No matches found',
      onSelect: options.onSelect || null,
      fetchUrl: options.fetchUrl || null,
      ...options
    };
    
    this.dropdown = null;
    this.selectedIndex = -1;
    this.isOpen = false;
    this.recentSelections = this.loadRecentSelections();
    
    this.init();
  }
  
  init() {
    // Remove any existing datalist reference
    this.input.removeAttribute('list');
    this.input.setAttribute('autocomplete', 'off');
    
    // Create dropdown container
    this.createDropdown();
    
    // Bind events
    this.bindEvents();
  }
  
  createDropdown() {
    // Create wrapper if input isn't already wrapped
    let wrapper = this.input.parentElement;
    if (!wrapper.classList.contains('smart-autocomplete-wrapper')) {
      wrapper = document.createElement('div');
      wrapper.className = 'smart-autocomplete-wrapper';
      this.input.parentNode.insertBefore(wrapper, this.input);
      wrapper.appendChild(this.input);
    }
    
    // Create dropdown
    this.dropdown = document.createElement('div');
    this.dropdown.className = 'smart-autocomplete-dropdown';
    this.dropdown.style.display = 'none';
    wrapper.appendChild(this.dropdown);
  }
  
  bindEvents() {
    // Input events
    this.input.addEventListener('input', (e) => this.onInput(e));
    this.input.addEventListener('focus', (e) => this.onFocus(e));
    this.input.addEventListener('blur', (e) => this.onBlur(e));
    this.input.addEventListener('keydown', (e) => this.onKeyDown(e));
    
    // Prevent form submission on enter when dropdown is open
    this.input.closest('form')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && this.isOpen && this.selectedIndex >= 0) {
        e.preventDefault();
      }
    });
  }
  
  onInput(e) {
    const value = e.target.value.trim();
    
    if (value.length < this.options.minChars) {
      this.close();
      return;
    }
    
    this.search(value);
  }
  
  onFocus(e) {
    const value = this.input.value.trim();
    if (value.length >= this.options.minChars) {
      this.search(value);
    } else if (this.recentSelections.length > 0) {
      // Show recent selections on focus with empty input
      this.showRecent();
    }
  }
  
  onBlur(e) {
    // Delay to allow click on dropdown item
    setTimeout(() => this.close(), 200);
  }
  
  onKeyDown(e) {
    if (!this.isOpen) {
      if (e.key === 'ArrowDown' && this.input.value.length >= this.options.minChars) {
        this.search(this.input.value);
      }
      return;
    }
    
    const items = this.dropdown.querySelectorAll('.smart-autocomplete-item:not(.empty-message)');
    
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
        this.updateSelection(items);
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
        this.updateSelection(items);
        break;
        
      case 'Enter':
        if (this.selectedIndex >= 0 && items[this.selectedIndex]) {
          e.preventDefault();
          this.selectItem(items[this.selectedIndex].dataset.value);
        }
        break;
        
      case 'Tab':
        if (this.selectedIndex >= 0 && items[this.selectedIndex]) {
          e.preventDefault();
          this.selectItem(items[this.selectedIndex].dataset.value);
        } else if (items.length > 0) {
          e.preventDefault();
          this.selectItem(items[0].dataset.value);
        }
        break;
        
      case 'Escape':
        this.close();
        break;
    }
  }
  
  updateSelection(items) {
    items.forEach((item, index) => {
      item.classList.toggle('selected', index === this.selectedIndex);
    });
    
    // Scroll selected item into view
    if (items[this.selectedIndex]) {
      items[this.selectedIndex].scrollIntoView({ block: 'nearest' });
    }
  }
  
  search(query) {
    const lowerQuery = query.toLowerCase();
    let data = this.options.dataSource;
    
    // Filter and score results
    let results = data
      .map(item => {
        const lowerItem = item.toLowerCase();
        let score = 0;
        
        // Exact match gets highest score
        if (lowerItem === lowerQuery) score = 100;
        // Starts with query
        else if (lowerItem.startsWith(lowerQuery)) score = 80;
        // Word starts with query
        else if (lowerItem.split(' ').some(word => word.startsWith(lowerQuery))) score = 60;
        // Contains query
        else if (lowerItem.includes(lowerQuery)) score = 40;
        else score = 0;
        
        // Boost recent selections
        if (this.options.showRecentFirst && this.recentSelections.includes(item)) {
          score += 20;
        }
        
        return { item, score };
      })
      .filter(r => r.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, this.options.maxResults)
      .map(r => r.item);
    
    this.renderResults(results, query);
  }
  
  showRecent() {
    const recentItems = this.recentSelections
      .filter(item => this.options.dataSource.includes(item))
      .slice(0, 5);
    
    if (recentItems.length > 0) {
      this.renderResults(recentItems, '', true);
    }
  }
  
  renderResults(results, query, isRecent = false) {
    this.dropdown.innerHTML = '';
    this.selectedIndex = -1;
    
    if (results.length === 0) {
      this.dropdown.innerHTML = `
        <div class="smart-autocomplete-item empty-message">
          <span class="autocomplete-icon">🔍</span>
          ${this.options.emptyMessage}
        </div>
      `;
    } else {
      if (isRecent) {
        this.dropdown.innerHTML = `
          <div class="smart-autocomplete-header">
            <span class="autocomplete-icon">🕐</span> Recent
          </div>
        `;
      }
      
      results.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'smart-autocomplete-item';
        div.dataset.value = item;
        
        // Highlight matching text
        let displayText = item;
        if (this.options.highlightMatches && query) {
          const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
          displayText = item.replace(regex, '<mark>$1</mark>');
        }
        
        const isRecentItem = this.recentSelections.includes(item);
        div.innerHTML = `
          ${isRecentItem && !isRecent ? '<span class="recent-indicator">●</span>' : ''}
          <span class="item-text">${displayText}</span>
        `;
        
        div.addEventListener('mousedown', (e) => {
          e.preventDefault();
          this.selectItem(item);
        });
        
        div.addEventListener('mouseenter', () => {
          this.selectedIndex = index;
          this.updateSelection(this.dropdown.querySelectorAll('.smart-autocomplete-item:not(.empty-message)'));
        });
        
        this.dropdown.appendChild(div);
      });
    }
    
    this.open();
  }
  
  selectItem(value) {
    this.input.value = value;
    this.addToRecent(value);
    this.close();
    
    // Trigger input event for any listeners
    this.input.dispatchEvent(new Event('input', { bubbles: true }));
    this.input.dispatchEvent(new Event('change', { bubbles: true }));
    
    if (this.options.onSelect) {
      this.options.onSelect(value);
    }
  }
  
  open() {
    this.dropdown.style.display = 'block';
    this.isOpen = true;
  }
  
  close() {
    this.dropdown.style.display = 'none';
    this.isOpen = false;
    this.selectedIndex = -1;
  }
  
  addToRecent(value) {
    // Remove if already exists, add to front
    this.recentSelections = this.recentSelections.filter(v => v !== value);
    this.recentSelections.unshift(value);
    this.recentSelections = this.recentSelections.slice(0, 10); // Keep last 10
    this.saveRecentSelections();
  }
  
  loadRecentSelections() {
    try {
      const key = `autocomplete_recent_${this.input.name || 'default'}`;
      return JSON.parse(localStorage.getItem(key)) || [];
    } catch {
      return [];
    }
  }
  
  saveRecentSelections() {
    try {
      const key = `autocomplete_recent_${this.input.name || 'default'}`;
      localStorage.setItem(key, JSON.stringify(this.recentSelections));
    } catch {}
  }
  
  escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  
  updateDataSource(data) {
    this.options.dataSource = data;
  }
}

// Initialize country autocomplete with smart system
function initCountryAutocomplete() {
  // Fetch existing countries from the database
  fetchExistingCountries().then(() => {
    // Setup smart autocomplete for all country inputs
    document.querySelectorAll('.country-autocomplete').forEach(input => {
      setupSmartCountryInput(input);
    });
  });
}

function fetchExistingCountries() {
  return fetch('/api/customers/countries')
    .then(response => response.json())
    .then(countries => {
      cachedCountries = countries;
      return countries;
    })
    .catch(error => {
      console.log('Using default countries list');
      cachedCountries = [];
      return [];
    });
}

function setupSmartCountryInput(input) {
  // Combine cached and default countries
  const allCountries = [...new Set([...cachedCountries, ...defaultCountries])].sort();
  
  // Create smart autocomplete instance
  const autocomplete = new SmartAutocomplete(input, {
    dataSource: allCountries,
    minChars: 1,
    maxResults: 10,
    placeholder: 'Start typing country...',
    emptyMessage: 'No countries found',
    highlightMatches: true,
    showRecentFirst: true
  });
  
  // Store reference for later updates
  input._smartAutocomplete = autocomplete;
}

// Legacy function compatibility - now does nothing as we use smart autocomplete
function updateAllCountryDatalists() {
  // Update all smart autocomplete instances with new data
  const allCountries = [...new Set([...cachedCountries, ...defaultCountries])].sort();
  document.querySelectorAll('.country-autocomplete').forEach(input => {
    if (input._smartAutocomplete) {
      input._smartAutocomplete.updateDataSource(allCountries);
    }
  });
}

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
  // Create toast container if it doesn't exist
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = `
      position: fixed;
      top: 70px;
      right: 20px;
      z-index: 10000;
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 400px;
      pointer-events: none;
    `;
    document.body.appendChild(toastContainer);
  }
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.style.cssText = `
    padding: 14px 20px;
    padding-right: 40px;
    background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    animation: slideInRight 0.3s ease-out;
    pointer-events: auto;
    position: relative;
    font-size: 14px;
    line-height: 1.5;
  `;
  
  const messageSpan = document.createElement('span');
  messageSpan.textContent = message;
  toast.appendChild(messageSpan);
  
  // Add close button
  const closeBtn = document.createElement('button');
  closeBtn.innerHTML = '×';
  closeBtn.style.cssText = `
    position: absolute;
    top: 50%;
    right: 12px;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.8;
    transition: opacity 0.2s;
  `;
  closeBtn.onmouseover = () => closeBtn.style.opacity = '1';
  closeBtn.onmouseout = () => closeBtn.style.opacity = '0.8';
  closeBtn.onclick = () => {
    toast.style.animation = 'slideOutRight 0.2s ease-out';
    setTimeout(() => toast.remove(), 200);
  };
  toast.appendChild(closeBtn);
  
  toastContainer.appendChild(toast);
  
  // Auto dismiss after 3 seconds
  const autoDismiss = setTimeout(() => {
    toast.style.animation = 'slideOutRight 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
  
  // Clear auto dismiss if manually closed
  closeBtn.onclick = () => {
    clearTimeout(autoDismiss);
    toast.style.animation = 'slideOutRight 0.2s ease-out';
    setTimeout(() => toast.remove(), 200);
  };
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
        const groupId = data.group_id || (groupField ? groupField.value : null);

        // Populate ALL groups organized by category and pre-select current group
        updateGroupSelect(categoryId, 'group_id', groupId);
        
        // Also set it after a delay to ensure groups are loaded
        if (groupId) {
          setTimeout(() => {
            const groupSelect = form.querySelector('select[name="group_id"]');
            if (groupSelect) {
              groupSelect.value = groupId;
            }
          }, 300);
        }

        // Ensure future category changes keep group list in sync.
        if (categoryField && !categoryField.dataset.groupHooked) {
          categoryField.addEventListener('change', function() {
            updateGroupSelect(this.value, 'group_id');
          });
          categoryField.dataset.groupHooked = 'true';
        }
        
        // Load customer subscriptions
        loadCustomerSubscriptions(id);
      }

      // Special handling: subscription edit needs customer dropdown populated based on category
      if (type === 'subscription') {
        const categoryField = form.querySelector('select[name="category_id"]');
        const customerField = form.querySelector('select[name="customer_id"]');
        const categoryId = categoryField ? categoryField.value : null;
        const customerId = data.customer_id;
        const saveBtn = form.querySelector('button[type="submit"]');

        // Function to load customers and update save button state
        const loadCustomersForCategory = (catId, selectedCustId) => {
          const url = selectedCustId 
            ? `/partials/customer-options?category_id=${catId}&selected_customer_id=${selectedCustId}`
            : `/partials/customer-options?category_id=${catId}`;
          
          fetch(url)
            .then(response => response.text())
            .then(html => {
              customerField.innerHTML = html;
              
              // Check if there are valid customers
              const options = customerField.querySelectorAll('option');
              const hasCustomers = Array.from(options).some(opt => opt.value && opt.value !== '');
              
              if (!hasCustomers) {
                // Disable save button if no customers available
                if (saveBtn) {
                  saveBtn.disabled = true;
                  saveBtn.title = 'No customers available in this category';
                }
              } else {
                // Re-enable save button if customers are available
                if (saveBtn) {
                  saveBtn.disabled = false;
                  saveBtn.title = '';
                }
              }
            })
            .catch(error => {
              console.error('Error loading customers:', error);
              customerField.innerHTML = '<option value="">Error loading customers</option>';
            });
        };

        // Load customers for the current category with preselection
        if (categoryId) {
          loadCustomersForCategory(categoryId, customerId);
        }

        // Listen for category changes to reload customers
        if (categoryField && !categoryField.dataset.customerHooked) {
          categoryField.addEventListener('change', function() {
            loadCustomersForCategory(this.value, null);
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

// Create Customer with comprehensive error handling
window.createCustomer = function(formData) {
  // Client-side validation first
  const validationErrors = [];
  
  if (!formData.name || !formData.name.trim()) {
    validationErrors.push('Customer name is required');
  }
  
  if (!formData.category_id) {
    validationErrors.push('Category is required');
  }
  
  if (!formData.country || !formData.country.trim()) {
    validationErrors.push('Country is required');
  }
  
  // Validate email format if provided
  if (formData.email && formData.email.trim()) {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(formData.email)) {
      validationErrors.push('Invalid email format');
    }
  }
  
  // Show validation errors and stop if any
  if (validationErrors.length > 0) {
    showToast('Validation Error: ' + validationErrors.join('; '), 'error');
    console.warn('Customer creation validation failed:', validationErrors);
    return;
  }
  
  // Prepare request payload
  const payload = {
    name: formData.name.trim(),
    category_id: parseInt(formData.category_id),
    group_id: formData.group_id ? parseInt(formData.group_id) : null,
    email: formData.email ? formData.email.trim() : null,
    phone: formData.phone ? formData.phone.trim() : null,
    country: formData.country.trim(),
    tags: formData.tags ? formData.tags.trim() : null,
    notes: formData.notes ? formData.notes.trim() : null
  };
  
  // Log request for debugging (no sensitive data)
  console.log('Creating customer with payload:', {
    ...payload,
    email: payload.email ? '[REDACTED]' : null
  });
  
  fetch('/api/customers', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  .then(response => {
    // Log response status for debugging
    console.log('Customer creation response:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      return response.json().then(err => {
        // Log full error details
        console.error('Customer creation failed:', {
          status: response.status,
          statusText: response.statusText,
          error: err,
          payload: { ...payload, email: payload.email ? '[REDACTED]' : null }
        });
        
        // Extract error message
        let errorMessage = 'Failed to create customer';
        if (err.detail) {
          errorMessage = typeof err.detail === 'string' 
            ? err.detail 
            : JSON.stringify(err.detail);
        } else if (err.message) {
          errorMessage = err.message;
        }
        
        throw new Error(errorMessage);
      }).catch(parseError => {
        // Handle JSON parse errors
        if (parseError.message && parseError.message !== 'Failed to create customer') {
          throw parseError;
        }
        console.error('Failed to parse error response:', parseError);
        throw new Error(`Server error (${response.status}): ${response.statusText}`);
      });
    }
    return response.json();
  })
  .then(data => {
    console.log('Customer created successfully:', { id: data.id, name: data.name });
    showToast('Customer created successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    // Show user-friendly error message
    const errorMsg = error.message || 'Unknown error occurred';
    showToast('Error: ' + errorMsg, 'error');
    console.error('Customer creation error:', error);
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
      country: formData.country || null,
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

// Update Customer with comprehensive error handling
window.updateCustomer = function(formData, id) {
  // Client-side validation first
  const validationErrors = [];
  
  if (!formData.name || !formData.name.trim()) {
    validationErrors.push('Customer name is required');
  }
  
  if (!formData.category_id) {
    validationErrors.push('Category is required');
  }
  
  // Validate email format if provided
  if (formData.email && formData.email.trim()) {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(formData.email)) {
      validationErrors.push('Invalid email format');
    }
  }
  
  // Show validation errors and stop if any
  if (validationErrors.length > 0) {
    showToast('Validation Error: ' + validationErrors.join('; '), 'error');
    console.warn('Customer update validation failed:', validationErrors);
    return;
  }
  
  // Prepare request payload
  const payload = {
    name: formData.name.trim(),
    category_id: parseInt(formData.category_id),
    group_id: formData.group_id ? parseInt(formData.group_id) : null,
    email: formData.email ? formData.email.trim() : null,
    phone: formData.phone ? formData.phone.trim() : null,
    country: formData.country ? formData.country.trim() : null,
    tags: formData.tags ? formData.tags.trim() : null,
    notes: formData.notes ? formData.notes.trim() : null
  };
  
  // Log request for debugging
  console.log('Updating customer with payload:', {
    id,
    ...payload,
    email: payload.email ? '[REDACTED]' : null
  });
  
  fetch(`/api/customers/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })
  .then(response => {
    console.log('Customer update response:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });
    
    if (!response.ok) {
      return response.json().then(err => {
        console.error('Customer update failed:', {
          status: response.status,
          error: err,
          customerId: id
        });
        
        let errorMessage = 'Failed to update customer';
        if (err.detail) {
          errorMessage = typeof err.detail === 'string' 
            ? err.detail 
            : JSON.stringify(err.detail);
        }
        throw new Error(errorMessage);
      }).catch(parseError => {
        if (parseError.message && parseError.message !== 'Failed to update customer') {
          throw parseError;
        }
        throw new Error(`Server error (${response.status}): ${response.statusText}`);
      });
    }
    return response.json();
  })
  .then(data => {
    console.log('Customer updated successfully:', { id: data.id, name: data.name });
    showToast('Customer updated successfully', 'success');
    closeAllModals();
    setTimeout(() => window.location.reload(), 500);
  })
  .catch(error => {
    const errorMsg = error.message || 'Unknown error occurred';
    showToast('Error: ' + errorMsg, 'error');
    console.error('Customer update error:', error);
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
      country: formData.country || null,
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

// Dynamic cascading selects - Shows ALL groups organized by category
window.updateGroupSelect = function(categoryId, groupSelectId = 'group_id', selectedGroupId = null) {
  // Find the group select - prefer searching within open modals first
  let groupSelect = null;
  
  // Try to find within an open modal (check both flex and block display)
  const openModals = document.querySelectorAll('.modal[style*="display: grid"], .modal[style*="display: flex"], .modal[style*="display: block"], .modal.show');
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
  
  // Fetch ALL groups and ALL categories to organize them
  Promise.all([
    fetch('/api/groups').then(r => r.json()),
    fetch('/api/categories').then(r => r.json())
  ])
    .then(([groups, categories]) => {
      groupSelect.innerHTML = '<option value="">No group</option>';
      
      // Create a map of category id to category name
      const categoryMap = {};
      categories.forEach(cat => {
        categoryMap[cat.id] = cat.name;
      });
      
      // Group the groups by category
      const groupsByCategory = {};
      groups.forEach(group => {
        const catId = group.category_id;
        if (!groupsByCategory[catId]) {
          groupsByCategory[catId] = [];
        }
        groupsByCategory[catId].push(group);
      });
      
      // Sort categories - put current category first if specified
      let sortedCategoryIds = Object.keys(groupsByCategory).map(Number);
      if (categoryId) {
        sortedCategoryIds.sort((a, b) => {
          if (a == categoryId) return -1;
          if (b == categoryId) return 1;
          return (categoryMap[a] || '').localeCompare(categoryMap[b] || '');
        });
      }
      
      // Create optgroups for each category
      sortedCategoryIds.forEach(catId => {
        const catGroups = groupsByCategory[catId];
        if (catGroups && catGroups.length > 0) {
          const optgroup = document.createElement('optgroup');
          const catName = categoryMap[catId] || 'Unknown Category';
          optgroup.label = catId == categoryId ? `📁 ${catName} (Current)` : `📁 ${catName}`;
          
          catGroups.forEach(group => {
            const option = document.createElement('option');
            option.value = group.id;
            option.textContent = group.name;
            if (selectedGroupId && String(group.id) === String(selectedGroupId)) {
              option.selected = true;
            }
            optgroup.appendChild(option);
          });
          
          groupSelect.appendChild(optgroup);
        }
      });
    })
    .catch(error => console.error('Error loading groups:', error));
};

window.updateCustomerSelect = function(categoryId, customerSelectId = 'customer_id', selectedCustomerId = null) {
  // Find the customer select - prefer searching within open modals first
  let customerSelect = null;
  
  // Try to find within an open modal
  const openModals = document.querySelectorAll('.modal[style*="display: grid"], .modal[style*="display: flex"], .modal.show');
  for (let modal of openModals) {
    const select = modal.querySelector(`select[name="${customerSelectId}"]`);
    if (select) {
      customerSelect = select;
      break;
    }
  }
  
  // Fallback to global search if not found in modals
  if (!customerSelect) {
    customerSelect = document.querySelector(`select[name="${customerSelectId}"]`);
  }
  
  if (!customerSelect) return;

  // Always load ALL customers to allow full selection flexibility
  fetch('/api/customers')
    .then(response => response.json())
    .then(customers => {
      customerSelect.innerHTML = '<option value="">Select a customer</option>';
      customers.forEach(customer => {
        const option = document.createElement('option');
        option.value = customer.id;
        // Show category info for context
        let categoryDisplay = '';
        if (customer.category_names) {
          categoryDisplay = ` (${customer.category_names})`;
        } else if (customer.categories && customer.categories.length > 0) {
          categoryDisplay = ` (${customer.categories.map(c => c.name).join(', ')})`;
        }
        option.textContent = customer.name + categoryDisplay;
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

// Update customer select specifically for edit subscription modal
window.updateCustomerSelectForEdit = function(categoryId) {
  const modal = document.getElementById('editSubscriptionModal');
  if (!modal) return;
  
  const customerSelect = modal.querySelector('select[name="customer_id"]');
  if (!customerSelect) return;
  
  const currentCustomerId = customerSelect.value;
  
  // Load all customers (not filtered by category) to allow reassignment
  fetch('/api/customers')
    .then(response => response.json())
    .then(customers => {
      customerSelect.innerHTML = '<option value="">Select a customer</option>';
      customers.forEach(customer => {
        const option = document.createElement('option');
        option.value = customer.id;
        // Use category_names for many-to-many relationships, fallback to categories array
        let categoryDisplay = 'No category';
        if (customer.category_names) {
          categoryDisplay = customer.category_names;
        } else if (customer.categories && customer.categories.length > 0) {
          categoryDisplay = customer.categories.map(c => c.name).join(', ');
        }
        option.textContent = `${customer.name} (${categoryDisplay})`;
        if (String(customer.id) === String(currentCustomerId)) {
          option.selected = true;
        }
        customerSelect.appendChild(option);
      });
    })
    .catch(error => {
      console.error('Error loading customers:', error);
    });
};

// Apply plan preset to plan name field
window.applyPlanPreset = function(preset) {
  if (!preset) return;
  
  const modal = document.getElementById('editSubscriptionModal');
  if (!modal) return;
  
  const planNameInput = modal.querySelector('input[name="plan_name"]');
  if (planNameInput) {
    const presetNames = {
      'basic': 'Basic',
      'standard': 'Standard',
      'professional': 'Professional',
      'enterprise': 'Enterprise',
      'custom': 'Custom'
    };
    planNameInput.value = presetNames[preset] || preset;
  }
};

// Update renewal date based on billing cycle change
window.updateRenewalDateFromCycle = function(cycle) {
  const modal = document.getElementById('editSubscriptionModal');
  if (!modal) return;
  
  const startDateInput = modal.querySelector('input[name="start_date"]');
  const renewalDateInput = modal.querySelector('input[name="next_renewal_date"]');
  
  if (!startDateInput || !renewalDateInput || !startDateInput.value) return;
  
  const startDate = new Date(startDateInput.value);
  let renewalDate = new Date(startDate);
  
  switch (cycle) {
    case 'weekly':
      renewalDate.setDate(renewalDate.getDate() + 7);
      break;
    case 'monthly':
      renewalDate.setMonth(renewalDate.getMonth() + 1);
      break;
    case 'quarterly':
      renewalDate.setMonth(renewalDate.getMonth() + 3);
      break;
    case 'biannual':
      renewalDate.setMonth(renewalDate.getMonth() + 6);
      break;
    case 'yearly':
      renewalDate.setFullYear(renewalDate.getFullYear() + 1);
      break;
  }
  
  // Format date as YYYY-MM-DD for input
  const formattedDate = renewalDate.toISOString().split('T')[0];
  renewalDateInput.value = formattedDate;
};

// ==================== Sidebar Toggle ====================
window.toggleSidebar = function() {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.classList.toggle('open');
  }
};

// Sidebar collapse feature removed

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

// ==================== Customer Subscriptions Management ====================
let currentEditingCustomerId = null;

window.loadCustomerSubscriptions = function(customerId) {
  currentEditingCustomerId = customerId;
  const container = document.getElementById('customer-subscriptions-list');
  if (!container) return;
  
  container.innerHTML = '<p class="text-secondary text-sm">Loading subscriptions...</p>';
  
  fetch(`/api/subscriptions?customer_id=${customerId}`)
    .then(response => response.json())
    .then(subscriptions => {
      if (subscriptions.length === 0) {
        container.innerHTML = `
          <div class="text-center py-3" style="background: var(--color-bg-secondary); border-radius: var(--radius-md);">
            <p class="text-secondary text-sm mb-2">No subscriptions yet</p>
            <button type="button" class="btn btn-sm btn-primary" onclick="addSubscriptionForCustomer()">+ Add First Subscription</button>
          </div>
        `;
        return;
      }
      
      container.innerHTML = subscriptions.map(sub => `
        <div class="flex items-center justify-between p-3 rounded-lg" style="background: var(--color-bg-secondary);">
          <div class="flex-1">
            <div class="font-medium">${sub.vendor_name}</div>
            <div class="text-sm text-secondary">
              $${parseFloat(sub.cost).toFixed(2)} / ${sub.billing_cycle} 
              <span class="badge badge-${sub.status === 'active' ? 'success' : sub.status === 'paused' ? 'warning' : 'secondary'}" style="margin-left: 8px;">${sub.status}</span>
            </div>
          </div>
          <div class="flex gap-1">
            <button type="button" class="btn btn-sm btn-secondary" onclick="editSubscriptionFromCustomer(${sub.id})" title="Edit">✏️</button>
            <a href="/subscriptions/${sub.id}" class="btn btn-sm btn-secondary" title="View">👁️</a>
          </div>
        </div>
      `).join('');
    })
    .catch(error => {
      console.error('Error loading subscriptions:', error);
      container.innerHTML = '<p class="text-secondary text-sm">Error loading subscriptions</p>';
    });
};

window.addSubscriptionForCustomer = function() {
  if (!currentEditingCustomerId) {
    showToast('Please save the customer first', 'warning');
    return;
  }
  
  // Close the edit customer modal
  closeModal('editCustomerModal');
  
  // Open subscription modal and pre-fill customer
  setTimeout(() => {
    openModal('subscriptionModal');
    
    // Fetch customer to get category
    fetch(`/api/customers/${currentEditingCustomerId}`)
      .then(response => response.json())
      .then(customer => {
        const form = document.querySelector('#subscriptionModal form');
        const categorySelect = form.querySelector('select[name="category_id"]');
        const customerSelect = form.querySelector('select[name="customer_id"]');
        
        if (categorySelect) {
          categorySelect.value = customer.category_id;
          // Load customers for this category
          updateCustomerSelect(customer.category_id, 'customer_id', currentEditingCustomerId);
        }
      })
      .catch(error => console.error('Error:', error));
  }, 350);
};

window.editSubscriptionFromCustomer = function(subscriptionId) {
  // Close customer modal and open subscription edit
  closeModal('editCustomerModal');
  setTimeout(() => {
    loadEditData('subscription', subscriptionId);
  }, 350);
};

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
  const model = localStorage.getItem('ai-model') || 'gemini-2.0-flash';
  const enabled = localStorage.getItem('ai-enabled') === 'true';
  
  const apiKeyInput = document.getElementById('ai-api-key');
  const modelSelect = document.getElementById('ai-model');
  const enabledCheckbox = document.getElementById('ai-enabled');
  
  if (apiKeyInput) apiKeyInput.value = apiKey;
  if (modelSelect) modelSelect.value = model;
  if (enabledCheckbox) enabledCheckbox.checked = enabled;
};

// ==================== Email Notification Functions ====================

// Send renewal notice for a subscription
window.sendRenewalNotice = function(subscriptionId) {
  if (!confirm('Send renewal notice email to the customer?')) {
    return;
  }
  
  showToast('Sending renewal notice...', 'info');
  
  fetch(`/api/email/renewal-notice/${subscriptionId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(err => {
        throw new Error(err.detail || 'Failed to send renewal notice');
      });
    }
    return response.json();
  })
  .then(data => {
    showToast(`✅ Renewal notice sent to ${data.recipient}`, 'success');
  })
  .catch(error => {
    showToast('Error: ' + error.message, 'error');
    console.error('Send renewal notice error:', error);
  });
};

// Send renewal notice to a custom email address
window.sendRenewalNoticeWithEmail = function(subscriptionId) {
  const email = prompt('Enter email address to send renewal notice to:');
  if (!email) return;
  
  // Validate email format
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailPattern.test(email)) {
    showToast('Invalid email format', 'error');
    return;
  }
  
  showToast('Sending renewal notice...', 'info');
  
  fetch(`/api/email/renewal-notice/${subscriptionId}?override_email=${encodeURIComponent(email)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(err => {
        throw new Error(err.detail || 'Failed to send renewal notice');
      });
    }
    return response.json();
  })
  .then(data => {
    showToast(`✅ Renewal notice sent to ${data.recipient}`, 'success');
  })
  .catch(error => {
    showToast('Error: ' + error.message, 'error');
    console.error('Send renewal notice error:', error);
  });
};

// View notice history for a subscription
window.viewNoticeHistory = function(subscriptionId) {
  fetch(`/api/email/renewal-notices?subscription_id=${subscriptionId}`)
    .then(response => response.json())
    .then(notices => {
      if (notices.length === 0) {
        showToast('No renewal notices have been sent for this subscription', 'info');
        return;
      }
      
      // Create a simple modal to display history
      let historyHtml = '<div style="max-height: 400px; overflow-y: auto;">';
      historyHtml += '<table style="width: 100%; border-collapse: collapse;">';
      historyHtml += '<tr style="border-bottom: 1px solid var(--color-border);"><th style="text-align: left; padding: 8px;">Date</th><th style="text-align: left; padding: 8px;">Recipient</th><th style="text-align: left; padding: 8px;">Status</th></tr>';
      
      notices.forEach(notice => {
        const date = new Date(notice.sent_at).toLocaleString();
        const status = notice.success ? '✅ Sent' : `❌ Failed: ${notice.error_message || 'Unknown error'}`;
        historyHtml += `<tr style="border-bottom: 1px solid var(--color-border);">
          <td style="padding: 8px;">${date}</td>
          <td style="padding: 8px;">${notice.recipient_email || 'N/A'}</td>
          <td style="padding: 8px;">${status}</td>
        </tr>`;
      });
      
      historyHtml += '</table></div>';
      
      // Show in an alert for now (could be improved with a proper modal)
      const historyWindow = window.open('', 'Notice History', 'width=600,height=400');
      historyWindow.document.write(`
        <html>
        <head>
          <title>Renewal Notice History</title>
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f5f5f5; }
          </style>
        </head>
        <body>
          <h2>📧 Renewal Notice History</h2>
          ${historyHtml}
        </body>
        </html>
      `);
    })
    .catch(error => {
      showToast('Error loading notice history', 'error');
      console.error('Load notice history error:', error);
    });
};

// Check email configuration status
window.checkEmailConfig = function() {
  fetch('/api/email/config')
    .then(response => response.json())
    .then(config => {
      if (config.configured) {
        showToast(`Email configured: ${config.from_email}`, 'success');
      } else {
        showToast('Email not configured. Set SMTP_USER and SMTP_PASSWORD in environment.', 'warning');
      }
    })
    .catch(error => {
      showToast('Error checking email config', 'error');
    });
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
  loadAIConfig,
  sendRenewalNotice,
  sendRenewalNoticeWithEmail,
  viewNoticeHistory,
  checkEmailConfig
};
