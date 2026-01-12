# Implementation Plan - Customer Flexibility & Email Renewal System

## Status Summary

### ✅ Completed (Tasks 1-3)
1. **Data Model Updates** - Many-to-many relationships implemented
2. **Database Migration** - Created migration for association tables
3. **API Endpoints** - Customer endpoints support multiple categories/groups

### 🔄 In Progress
4. **UI Updates** - Need to update forms for multiple selections

### ⏳ Pending (Tasks 5-8)
5. **Email Renewal Notice System**
6. **Bulk Renewal Notices**
7. **Reports Updates**
8. **Category Dashboard Interactivity**

---

## What Has Been Implemented

### 1. Database Schema Changes
- Created `customer_categories` association table (many-to-many)
- Created `customer_groups` association table (many-to-many)
- Updated Customer model to support both legacy and new relationships
- Migration script handles backward compatibility

### 2. API Changes
- `POST /api/customers` - Accepts `category_ids[]` and `group_ids[]`
- `PUT /api/customers/{id}` - Supports updating multiple categories/groups
- `GET /api/customers` - Filters work with many-to-many relationships
- Backward compatible with single category/group

### 3. Schema Updates
- CustomerCreate/Update schemas support both single and multiple
- CustomerResponse includes full category and group lists
- Helper properties: `category_names`, `group_names`

---

## Next Steps Required

### Phase 1: UI Updates (Task 4)
**Files to modify:**
- `app/templates/base.html` - Customer modal forms
- `app/templates/customers_page.html` - Display multiple categories/groups
- `static/js/app.js` - JavaScript for multi-select handling

**Changes needed:**
1. Replace single `<select>` with multi-select for categories
2. Replace single `<select>` with multi-select for groups
3. Add visual chips/badges for selected items
4. Update JavaScript to handle arrays instead of single values
5. Update customer list display to show all categories/groups

### Phase 2: Email System (Task 5)
**New files to create:**
- `app/models/email_config.py` - SMTP configuration model
- `app/services/email_service.py` - Email sending service
- `app/routers/email_routes.py` - Email API endpoints
- `app/templates/email_renewal_notice.html` - Email template

**Features:**
- SMTP configuration stored in database
- Send renewal notice to single customer
- Email preview before sending
- Email tracking/logging

### Phase 3: Bulk Email System (Task 6)
**Files to modify/create:**
- `app/routers/subscriptions.py` - Add bulk operations
- `app/templates/subscriptions_page.html` - Bulk selection UI
- `static/js/app.js` - Bulk selection logic

**Features:**
- Select multiple subscriptions (checkboxes)
- Filter before sending (category, group, date range)
- Preview recipients and email content
- Confirmation dialog before sending
- Progress indicator for bulk sends

### Phase 4: Enhanced Reports (Task 7)
**Files to modify:**
- `app/routers/export_routes.py` - Update export logic
- `app/templates/reports.html` - New report sections

**Report sections to add:**
- Customers with multiple subscriptions
- Cross-category customer analysis
- Multi-group customer breakdown
- Subscription distribution across categories

### Phase 5: Interactive Category Dashboard (Task 8)
**Files to modify:**
- `app/templates/category_detail.html` - Add interactive cards
- `app/templates/dashboard.html` - Reference for card design
- `static/js/app.js` - Click handlers for cards

**Features:**
- Clickable stat cards (like main dashboard)
- Filtered views for expiring/overdue
- Quick action buttons on filtered views
- Consistent design with main dashboard

---

## Database Migration Instructions

To apply the many-to-many relationships:

```bash
# Review the migration
cat alembic/versions/add_many_to_many_relationships.py

# Run the migration
alembic upgrade head

# If issues occur, rollback
alembic downgrade -1
```

The migration will:
1. Create association tables
2. Copy existing data to new tables
3. Make category_id nullable (keep for compatibility)
4. Make country field required

---

## Testing Checklist

### API Testing
- [ ] Create customer with single category (legacy)
- [ ] Create customer with multiple categories
- [ ] Create customer with multiple groups
- [ ] Update customer categories/groups
- [ ] List customers filtered by category
- [ ] List customers filtered by group
- [ ] Verify backward compatibility

### UI Testing (After Phase 1)
- [ ] Multi-select categories works
- [ ] Multi-select groups works
- [ ] Selected items show as chips/badges
- [ ] Removing selections works
- [ ] Form validation works
- [ ] Customer list shows all categories/groups

### Email Testing (After Phase 2)
- [ ] SMTP configuration can be saved
- [ ] Email preview displays correctly
- [ ] Single renewal notice sends
- [ ] Recipient receives email
- [ ] Email content is correct

### Bulk Email Testing (After Phase 3)
- [ ] Multiple subscriptions can be selected
- [ ] Filtering works correctly
- [ ] Preview shows all recipients
- [ ] Bulk send completes successfully
- [ ] Progress indicator updates

---

## Important Notes

### Backward Compatibility
- Legacy `category_id` and `group_id` fields maintained
- Old API calls still work
- Existing data automatically migrated
- No breaking changes for existing code

### Performance Considerations
- Use `lazy="selectin"` for relationships (already configured)
- Consider pagination for large customer lists
- Index association table columns (done)
- Batch email sending to avoid timeouts

### Security Considerations
- SMTP credentials should be encrypted
- Email rate limiting to prevent spam
- Validate all email addresses
- Sanitize email content to prevent injection

---

## Estimated Effort

| Phase | Description | Complexity | Est. Time |
|-------|-------------|------------|-----------|
| 1 | UI Updates | Medium | 2-3 hours |
| 2 | Email System | High | 4-5 hours |
| 3 | Bulk Email | Medium | 2-3 hours |
| 4 | Reports | Medium | 2-3 hours |
| 5 | Dashboard | Low | 1-2 hours |

**Total: 11-16 hours**

---

## Current Status

✅ **Core data model and API are complete and ready to use**
- Many-to-many relationships fully implemented
- Migration script ready to run
- API endpoints support new features
- Backward compatible with existing code

🔄 **Next immediate step: Run the migration**
```bash
alembic upgrade head
```

Then choose which phase to tackle next based on priority.
