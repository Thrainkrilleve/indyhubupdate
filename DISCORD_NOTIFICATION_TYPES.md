# Discord Role-Based Notifications - Implementation Update

## 🎯 What Changed

Updated the Discord role-based notification system to support **separate role configurations** for different notification types.

## 📋 Notification Types

### 1. Industry Notifications
**Setting:** `INDY_HUB_DISCORD_NOTIFICATION_ROLES`

Applies to:
- ✅ Blueprint job completions
- ✅ Blueprint copy requests/offers
- ✅ Blueprint copy deliveries
- ✅ Industry job notifications

### 2. Material Exchange Admin Notifications
**Setting:** `INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES`

Applies to:
- ✅ New buy orders to review
- ✅ New sell orders to review
- ✅ Admin-level Material Exchange notifications

### 3. User-Specific Notifications
**No filtering** - Always sent to the user

Applies to:
- ✅ Your order was approved
- ✅ Your order was rejected
- ✅ Your order was delivered
- ✅ Any notification about YOUR orders/activity

## 🔧 Configuration Examples

### Separate Teams

```python
# Industry team only gets industry notifications
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {"name": "Industry Team", "enabled": True},
}

# Material Exchange team only gets Material Exchange admin notifications
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "9876543210987654321": {"name": "Material Exchange Managers", "enabled": True},
}

DISCORD_GUILD_ID = 123456789012345678
```

### Combined Team

```python
# Same role gets both types of notifications
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "5555555555555555555": {"name": "Operations Team", "enabled": True},
}

INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "5555555555555555555": {"name": "Operations Team", "enabled": True},
}
```

### Multiple Roles Per Type

```python
# Multiple roles can receive industry notifications
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1111111111111111111": {"name": "Industry Team", "enabled": True},
    "2222222222222222222": {"name": "Leadership", "enabled": True},
}

# Different roles can receive Material Exchange notifications
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "3333333333333333333": {"name": "Finance Team", "enabled": True},
    "4444444444444444444": {"name": "Logistics", "enabled": True},
}
```

### Disable One, Keep the Other

```python
# All users with permission get industry notifications
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {}

# Only Material Exchange Managers role gets Material Exchange notifications
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "9876543210987654321": {"name": "Material Exchange Managers", "enabled": True},
}
```

## 🚀 How It Works

### Technical Flow

```
Notification triggered
    ↓
Check notification_type parameter
    ↓
If "industry" → Check INDY_HUB_DISCORD_NOTIFICATION_ROLES
If "material_exchange" → Check INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES
If "user" → Skip role check, always send
    ↓
Get user's Discord roles from guild
    ↓
Does user have ANY of the required roles?
    ↓
Yes → Send notification
No  → Skip notification (logged)
```

### Code Integration

**In `discord_roles.py`:**
- Added `notification_type` parameter to all functions
- Added constants: `NOTIFICATION_TYPE_INDUSTRY`, `NOTIFICATION_TYPE_MATERIAL_EXCHANGE`, `NOTIFICATION_TYPE_USER`
- `get_notification_roles(notification_type)` - Returns correct setting based on type
- `user_has_notification_role(user, notification_type)` - Checks roles for that type
- `filter_users_by_notification_role(users, notification_type)` - Filters user list

**In `notifications.py`:**
- Added `notification_type` parameter to `notify_user()` (defaults to "industry")
- Added `notification_type` parameter to `notify_multi()` (defaults to "industry")
- Functions now pass the type to role checking utilities

**In `material_exchange.py`:**
- Admin notifications: `notification_type="material_exchange"`
- User notifications: `notification_type="user"`

## ✅ Benefits

1. **Separation of Concerns**
   - Industry managers only get industry notifications
   - Material Exchange managers only get Material Exchange notifications
   - Teams don't get spammed with irrelevant notifications

2. **User Privacy**
   - Users ALWAYS receive their own order status updates
   - No admin can block user notifications with role configuration

3. **Flexible Configuration**
   - Can use same role for both types
   - Can use different roles for each type
   - Can disable one and keep the other
   - Multiple roles per type (OR logic)

4. **Backward Compatible**
   - If neither setting configured → everyone gets notifications (original behavior)
   - Industry notifications still work with existing `INDY_HUB_DISCORD_NOTIFICATION_ROLES`
   - Material Exchange notifications still work if setting not defined

## 🧪 Testing

### Test Industry Notifications

```python
from indy_hub.utils.discord_roles import user_has_notification_role, NOTIFICATION_TYPE_INDUSTRY
from django.contrib.auth.models import User

user = User.objects.get(username='industry_manager')
has_role = user_has_notification_role(user, NOTIFICATION_TYPE_INDUSTRY)
print(f"Can receive industry notifications: {has_role}")
```

### Test Material Exchange Notifications

```python
from indy_hub.utils.discord_roles import user_has_notification_role, NOTIFICATION_TYPE_MATERIAL_EXCHANGE
from django.contrib.auth.models import User

user = User.objects.get(username='mat_exchange_manager')
has_role = user_has_notification_role(user, NOTIFICATION_TYPE_MATERIAL_EXCHANGE)
print(f"Can receive Material Exchange notifications: {has_role}")
```

### Test User Notifications

```python
from indy_hub.utils.discord_roles import user_has_notification_role, NOTIFICATION_TYPE_USER
from django.contrib.auth.models import User

user = User.objects.get(username='regular_user')
has_role = user_has_notification_role(user, NOTIFICATION_TYPE_USER)
print(f"Can receive user notifications: {has_role}")  # Always True
```

## 📝 Migration Guide

### From Old System

If you already have:
```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {"name": "Industry Team", "enabled": True},
}
```

**No changes needed!** This still works for industry notifications.

To add Material Exchange filtering:
```python
# Keep existing industry configuration
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {"name": "Industry Team", "enabled": True},
}

# Add Material Exchange configuration
INDY_HUB_MATERIAL_EXCHANGE_NOTIFICATION_ROLES = {
    "9876543210987654321": {"name": "Material Exchange Managers", "enabled": True},
}
```

## 🔍 Debug Logging

Enable detailed logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'indy_hub.utils.discord_roles': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
        'indy_hub.notifications': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

Look for log messages like:
```
DEBUG - User john_doe has industry notification role
DEBUG - User jane_doe does not have material_exchange notification role
DEBUG - Skipping material_exchange notification for jane_doe - no notification role
```

## ❓ FAQ

**Q: Do users still get their own order status updates?**
A: Yes! User-specific notifications (`notification_type="user"`) are NEVER filtered. Users always receive notifications about their own orders.

**Q: Can I use the same role for both notification types?**
A: Yes! Just configure the same role ID in both settings.

**Q: What happens if I don't configure Material Exchange roles?**
A: All users with `can_manage_material_hub` permission receive Material Exchange admin notifications (default behavior).

**Q: What happens if I don't configure Industry roles?**
A: All users with Indy Hub access receive industry notifications (default behavior).

**Q: Can a user be in one team but not the other?**
A: Absolutely! That's the whole point. Industry managers only see industry notifications, Material Exchange managers only see Material Exchange notifications.

**Q: How do I test this?**
A: Check your Discord role IDs, configure the settings, restart services, and place a test order. Check the logs to see role filtering in action.

## 🎉 Summary

✅ Separate role configurations for Industry and Material Exchange
✅ User notifications always sent (no filtering)
✅ Flexible team management
✅ Backward compatible
✅ No main file changes required - all in `discord_roles.py` utility
