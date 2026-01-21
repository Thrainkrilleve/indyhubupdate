# Discord Role-Based Notifications Setup

This guide explains how to configure Indy Hub to only send Discord notifications to users with specific Discord roles, following the pattern from [BlackhawkGT/auth-scripts](https://github.com/BlackhawkGT/auth-scripts).

## 📋 What This Does

Allows you to restrict Discord notifications to specific Discord roles (e.g., "Industry Team", "Leadership", etc.) instead of notifying all users.

## ⚙️ Prerequisites

- `aa-discordbot` or `aa-discordnotify` installed and configured
- Discord bot properly connected to your Alliance Auth
- Users have linked their Discord accounts in Alliance Auth

## 🚀 Quick Start

### Step 1: Find Your Discord Role IDs

1. Enable Developer Mode in Discord:
   - Settings → App Settings → Advanced → Developer Mode (ON)

2. Right-click on a role in your Discord server → Copy ID

3. Example role IDs:
   - Industry Team: `1234567890123456789`
   - Leadership: `9876543210987654321`

### Step 2: Add Roles Using Management Command

```bash
# Add a single role
python manage.py manage_discord_notification_roles add --role-id 1234567890123456789 --role-name "Industry Team"

# Add another role
python manage.py manage_discord_notification_roles add --role-id 9876543210987654321 --role-name "Leadership"

# List all configured roles
python manage.py manage_discord_notification_roles list
```

### Step 3: Update Your local.py Settings

The management command will generate the settings snippet for you. Add it to your `local.py`:

```python
# Discord Notification Roles Configuration
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": True,
    },
    "9876543210987654321": {
        "name": "Leadership",
        "enabled": True,
    },
}
```

### Step 4: Restart Your Services

```bash
# If using Docker
docker compose restart allianceauth_worker allianceauth_beat allianceauth_gunicorn

# If using systemd
systemctl restart allianceauth-worker
systemctl restart allianceauth-beat
systemctl restart allianceauth-gunicorn
```

## 📖 Management Commands Reference

### List Configured Roles

```bash
python manage.py manage_discord_notification_roles list
```

Output:
```
📋 Configured Discord Notification Roles:
======================================================================

Role ID: 1234567890123456789
Name:    Industry Team
Status:  ✓ Enabled
----------------------------------------------------------------------

Role ID: 9876543210987654321
Name:    Leadership
Status:  ✓ Enabled
----------------------------------------------------------------------

Total roles: 2
```

### Add a New Role

```bash
python manage.py manage_discord_notification_roles add \
    --role-id 1234567890123456789 \
    --role-name "Industry Team"
```

### Remove a Role

```bash
python manage.py manage_discord_notification_roles remove \
    --role-id 1234567890123456789
```

### Clear All Roles

```bash
python manage.py manage_discord_notification_roles clear
```

This will disable role-based filtering and notify all users again.

## 🔧 Advanced Configuration

### Temporarily Disable a Role

Edit your `local.py` and set `enabled: False`:

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": False,  # Temporarily disabled
    },
}
```

### Multiple Roles (OR Logic)

Users with **any** of the configured roles will receive notifications:

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1111111111111111111": {"name": "Industry Team", "enabled": True},
    "2222222222222222222": {"name": "Leadership", "enabled": True},
    "3333333333333333333": {"name": "Manufacturers", "enabled": True},
}
```

A user only needs **one** of these roles to receive notifications.

## 🧪 Testing

### Test Role Filtering

```bash
# Check if role filtering is enabled
python manage.py shell
>>> from indy_hub.utils.discord_roles import is_notification_enabled, get_enabled_role_ids
>>> is_notification_enabled()
True
>>> get_enabled_role_ids()
['1234567890123456789', '9876543210987654321']
```

### Test User Role Check

```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from indy_hub.utils.discord_roles import user_has_notification_role
>>> user = User.objects.get(username='your_username')
>>> user_has_notification_role(user)
True
```

## 🔍 How It Works

### Notification Flow

1. **Check if role filtering is enabled**
   - If `INDY_HUB_DISCORD_NOTIFICATION_ROLES` is empty → notify everyone
   - If configured → check user's roles

2. **Get user's Discord account**
   - Looks up user's linked Discord account
   - Gets their Discord member object from the guild

3. **Check user's roles**
   - Compares user's Discord roles against configured notification roles
   - If user has any matching role → send notification
   - If no matching roles → skip notification

4. **Error handling**
   - If Discord bot is unavailable → notify everyone (fail-safe)
   - If user's Discord account not found → skip notification
   - Logs all actions for debugging

### Integration Points

The role filtering integrates with existing notification functions:

**Before (notifications.py)**:
```python
def notify_user(user, title, message, level="info", **kwargs):
    # Sends to everyone
```

**After (with role filtering)**:
```python
from indy_hub.utils.discord_roles import user_has_notification_role

def notify_user(user, title, message, level="info", **kwargs):
    # Check if user should receive notification
    if not user_has_notification_role(user):
        logger.debug(f"Skipping notification for {user} - no notification role")
        return
    
    # Original notification logic...
```

## ❓ Troubleshooting

### Notifications Not Being Filtered

**Check role configuration:**
```bash
python manage.py manage_discord_notification_roles list
```

**Verify aadiscordbot is installed:**
```bash
pip list | grep aadiscordbot
```

**Check Discord Guild ID:**
```python
# In local.py
DISCORD_GUILD_ID = 123456789012345678
```

### Users Not Receiving Notifications

**Check if user has linked Discord:**
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> hasattr(user, 'discord')
True
```

**Check if user has the correct role in Discord:**
- Use Discord's member list to verify roles
- Ensure role IDs match exactly

**Check logs:**
```bash
# Docker
docker logs allianceauth_worker | grep "notification"

# Systemd
journalctl -u allianceauth-worker | grep "notification"
```

### Role Filtering Not Working

**Common issues:**
1. `DISCORD_GUILD_ID` not set in `local.py`
2. Discord bot not connected to guild
3. User's Discord account not linked in Alliance Auth
4. Role ID typo (role IDs are very long numbers)

**Debug logging:**
```python
# In local.py, add:
LOGGING = {
    'loggers': {
        'indy_hub.utils.discord_roles': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## 📝 Examples

### Example 1: Industry Team Only

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": True,
    },
}
```

### Example 2: Multiple Teams

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1111111111111111111": {"name": "Industry Team", "enabled": True},
    "2222222222222222222": {"name": "Leadership", "enabled": True},
    "3333333333333333333": {"name": "Manufacturers", "enabled": True},
    "4444444444444444444": {"name": "Logistics", "enabled": True},
}
```

### Example 3: Disable for Testing

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": False,  # Disabled for testing
    },
}
```

## 🔗 Related Links

- [BlackhawkGT/auth-scripts](https://github.com/BlackhawkGT/auth-scripts) - Inspiration for this feature
- [Alliance Auth Discord Documentation](https://allianceauth.readthedocs.io/en/latest/features/services/discord.html)
- [aa-discordbot GitHub](https://github.com/pvyParts/allianceauth-discordbot)

## 💡 Notes

- **Fail-safe behavior**: If role checking fails, notifications are sent to avoid blocking users
- **Performance**: Role checks are done at notification time (minimal overhead)
- **Compatibility**: Works with both `aadiscordbot` and `aa-discordnotify`
- **Persistence**: Settings persist across container restarts and rebuilds

## 🎉 That's It!

You've successfully configured role-based Discord notifications following the BlackhawkGT/auth-scripts pattern!

Need help? Check the troubleshooting section or review your logs.
