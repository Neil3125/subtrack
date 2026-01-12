# Quick Reference - Multi-Category Customer System

## 🎯 What's Been Completed

### Core Infrastructure (100% Complete)
✅ Database schema supports many-to-many relationships  
✅ Customer ↔ Categories (multiple)  
✅ Customer ↔ Groups (multiple)  
✅ Backward compatible with existing single relationships  
✅ API endpoints fully updated  
✅ Country field now required  

---

## 🚀 How to Use the New Features

### API Examples

#### Create Customer with Multiple Categories
```bash
POST /api/customers
{
  "name": "John Doe",
  "email": "john@example.com",
  "country": "United States",
  "category_ids": [1, 2, 3],    # Multiple categories
  "group_ids": [5, 7]            # Multiple groups
}
```

#### Create Customer (Legacy - Single Category)
```bash
POST /api/customers
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "country": "Canada",
  "category_id": 1,              # Single category (still works)
  "group_id": 5                  # Single group (still works)
}
```

#### Update Customer Categories/Groups
```bash
PUT /api/customers/123
{
  "category_ids": [1, 2, 4],     # Replace all categories
  "group_ids": [6, 8, 9]         # Replace all groups
}
```

#### Query Customers by Category/Group
```bash
GET /api/customers?category_id=1   # All customers in category 1
GET /api/customers?group_id=5       # All customers in group 5
GET /api/customers?country=USA      # All customers in USA
```

---

## 📊 Customer Response Format

```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "country": "United States",
  
  // Legacy fields (for compatibility)
  "category_id": 1,
  "group_id": 5,
  
  // New many-to-many relationships
  "categories": [
    {"id": 1, "name": "Software"},
    {"id": 2, "name": "Cloud Services"},
    {"id": 3, "name": "Marketing"}
  ],
  "groups": [
    {"id": 5, "name": "Enterprise Clients"},
    {"id": 7, "name": "Monthly Billing"}
  ],
  
  // Helper properties
  "category_names": "Software, Cloud Services, Marketing",
  "group_names": "Enterprise Clients, Monthly Billing"
}
```

---

## 🗃️ Database Schema

### New Association Tables

**customer_categories**
| customer_id | category_id |
|-------------|-------------|
| 1           | 1           |
| 1           | 2           |
| 2           | 1           |

**customer_groups**
| customer_id | group_id |
|-------------|----------|
| 1           | 5        |
| 1           | 7        |
| 2           | 5        |

### Updated Customers Table
- `category_id` - Still exists, nullable (for compatibility)
- `group_id` - Still exists, nullable (for compatibility)
- `country` - **Now REQUIRED** (not nullable)

---

## 🔧 Migration Instructions

### Step 1: Review Migration
```bash
cat alembic/versions/add_many_to_many_relationships.py
```

### Step 2: Apply Migration
```bash
alembic upgrade head
```

### Step 3: Verify
```python
# In Python shell
from app.database import SessionLocal
from app.models import Customer

db = SessionLocal()
customer = db.query(Customer).first()
print(f"Categories: {[c.name for c in customer.categories]}")
print(f"Groups: {[g.name for g in customer.groups]}")
```

### Rollback (if needed)
```bash
alembic downgrade -1
```

---

## 📋 What Still Needs Implementation

### Priority 1: UI Updates (2-3 hours)
**Goal:** Multi-select dropdowns for categories/groups

**Files to modify:**
- `app/templates/base.html` - Customer modals
- `app/templates/customers_page.html` - Customer list display
- `static/js/app.js` - JavaScript handlers

**Changes:**
```html
<!-- Replace single select -->
<select name="category_id">...</select>

<!-- With multi-select -->
<select name="category_ids" multiple class="multi-select">
  <option value="1">Software</option>
  <option value="2">Cloud Services</option>
</select>
```

Add JavaScript:
```javascript
// Handle multi-select submissions
function createCustomer(formData) {
  const categoryIds = Array.from(
    document.querySelectorAll('[name="category_ids"] option:checked')
  ).map(opt => parseInt(opt.value));
  
  const data = {
    ...formData,
    category_ids: categoryIds
  };
  // Submit...
}
```

### Priority 2: Email Renewal System (4-5 hours)
**Goal:** Send renewal notices via SMTP

**New files needed:**
```
app/models/email_config.py        # SMTP settings
app/services/email_service.py     # Email logic
app/routers/email_routes.py       # API endpoints
app/templates/emails/
  renewal_notice.html             # Email template
  renewal_notice.txt              # Text version
```

**API Design:**
```python
POST /api/subscriptions/{id}/send-renewal-notice
{
  "preview": false,  # Set true to preview
  "custom_message": "..."  # Optional
}

Response:
{
  "success": true,
  "recipient": "customer@example.com",
  "preview_html": "...",  # If preview=true
  "sent_at": "2026-01-12T15:00:00Z"
}
```

### Priority 3: Bulk Email (2-3 hours)
**Goal:** Send to multiple customers at once

**Features:**
- Checkbox selection in subscription list
- Filter UI (category, date range, status)
- Preview all recipients before sending
- Confirmation dialog
- Progress indicator

**API Design:**
```python
POST /api/subscriptions/bulk-send-renewal-notices
{
  "subscription_ids": [1, 2, 3, 4, 5],
  "filters": {
    "category_ids": [1, 2],
    "expiring_within_days": 30
  },
  "preview": false
}

Response:
{
  "success": true,
  "sent_count": 5,
  "failed_count": 0,
  "recipients": ["email1@...", "email2@..."],
  "errors": []
}
```

### Priority 4: Enhanced Reports (2-3 hours)
**Goal:** Show multi-category/group relationships

**New report sections:**
1. Customers with Multiple Subscriptions
2. Cross-Category Analysis
3. Multi-Group Breakdown
4. Subscription Distribution

### Priority 5: Interactive Category Dashboard (1-2 hours)
**Goal:** Clickable cards like main dashboard

**Features:**
- Click "Expiring Soon" → filtered list
- Click "Overdue" → filtered list
- Click "Active" → filtered list
- Each filtered view has bulk actions

---

## 🧪 Testing Checklist

### Backend (Ready to Test Now)
```bash
# Test creating customer with multiple categories
curl -X POST http://localhost:8000/api/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "country": "USA",
    "category_ids": [1, 2],
    "group_ids": [1]
  }'

# Test querying
curl http://localhost:8000/api/customers?category_id=1

# Test updating
curl -X PUT http://localhost:8000/api/customers/1 \
  -H "Content-Type: application/json" \
  -d '{
    "category_ids": [1, 2, 3]
  }'
```

### Frontend (After UI Updates)
- [ ] Multi-select shows all categories
- [ ] Can select multiple categories
- [ ] Can select multiple groups
- [ ] Selected items show as badges/chips
- [ ] Removing selection works
- [ ] Form submits correctly
- [ ] Customer list shows all categories

---

## 💡 Pro Tips

### Querying Multiple Relationships
```python
# Get customers with subscriptions in multiple categories
customers_with_multiple = db.query(Customer).join(
    Customer.categories
).group_by(Customer.id).having(
    func.count(Category.id) > 1
).all()

# Get all subscriptions for a customer across categories
customer = db.query(Customer).get(1)
all_subs = customer.subscriptions  # Works across all categories
```

### Display in Templates
```html
<!-- Show all categories as badges -->
{% for category in customer.categories %}
  <span class="badge badge-primary">{{ category.name }}</span>
{% endfor %}

<!-- Or use the helper property -->
<span>{{ customer.category_names }}</span>
```

### Backward Compatibility
- Old code using `customer.category_id` still works
- New code should use `customer.categories` (list)
- Migration handles data conversion automatically

---

## ⚠️ Important Notes

1. **Run migration first** before using new features
2. **Country is now required** - ensure all forms validate it
3. **API is backward compatible** - single category_id still works
4. **UI needs updates** to show multiple categories/groups
5. **Email system is separate** - implement when ready

---

## 📞 Need Help?

Check the detailed implementation plan:
```bash
cat IMPLEMENTATION_PLAN.md
```

Review the migration:
```bash
cat alembic/versions/add_many_to_many_relationships.py
```

View model changes:
```bash
cat app/models/customer.py
cat app/models/associations.py
```
