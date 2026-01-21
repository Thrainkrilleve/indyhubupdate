# Discord Role-Based Notifications

> **Pattern Credit**: Inspired by [BlackhawkGT/auth-scripts](https://github.com/BlackhawkGT/auth-scripts)

## 📖 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Files Overview](#files-overview)
- [Requirements](#requirements)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Overview

This feature allows you to restrict Indy Hub Discord notifications to users with specific Discord roles, following the same patterns used in the BlackhawkGT/auth-scripts repository for Alliance Auth customizations.

**Key Benefits:**
- 🎯 Target notifications to relevant teams (Industry, Leadership, etc.)
- 🔧 Easy management via Django command-line tools
- 📊 No database changes required (settings-based)
- 🛡️ Fail-safe: errors allow notifications rather than blocking
- 🔄 Fully backward compatible with existing notification system

## Quick Start

### 1. Get Your Discord Role ID

In Discord:
```
Settings → Advanced → Developer Mode (ON)
Right-click role → Copy ID
```

### 2. Add the Role

```bash
python manage.py manage_discord_notification_roles add \
    --role-id 1234567890123456789 \
    --role-name "Industry Team"
```

### 3. Update Settings

Add the generated snippet to `local.py`:

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": True,
    },
}

DISCORD_GUILD_ID = 123456789012345678  # Your server ID
```

### 4. Restart

```bash
# Docker
docker compose restart

# Systemd
systemctl restart allianceauth-*
```

**Done!** Only users with the "Industry Team" role will now receive notifications.

## Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [DISCORD_ROLES_QUICKSTART.md](DISCORD_ROLES_QUICKSTART.md) | 5-minute setup guide | Everyone |
| [DISCORD_ROLES_SETUP.md](DISCORD_ROLES_SETUP.md) | Complete documentation | Admins |
| [discord_notification_roles_settings.py.example](discord_notification_roles_settings.py.example) | Configuration examples | Developers |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Technical details | Developers |

## Files Overview

### Core Files

```
indy_hub/
├── utils/
│   └── discord_roles.py                    # Role checking utilities
├── management/
│   └── commands/
│       └── manage_discord_notification_roles.py  # CLI management
└── notifications.py                        # Modified for role filtering

# Documentation
├── DISCORD_ROLES_QUICKSTART.md            # Quick start guide
├── DISCORD_ROLES_SETUP.md                 # Complete guide
├── discord_notification_roles_settings.py.example  # Config examples
└── IMPLEMENTATION_SUMMARY.md              # Technical details

# Testing
└── test_discord_roles.py                  # Validation script
```

### What Was Modified

| File | Change | Impact |
|------|--------|--------|
| `notifications.py` | Added role filtering | Notifications now check roles |
| `README.md` | Added documentation section | Users know feature exists |
| `CHANGELOG.md` | Documented new feature | Change tracking |

### What's New

- `discord_roles.py` - Role checking utilities
- `manage_discord_notification_roles.py` - Management command
- Documentation files (6 new files)
- Test script

## Requirements

### Mandatory

- Alliance Auth v4+
- Python 3.10+
- Indy Hub installed

### Optional (for role checking)

- `aa-discordbot` or `aa-discordnotify` installed
- Discord bot connected to your server
- Users have linked Discord accounts

### Configuration

- `DISCORD_GUILD_ID` in settings (required for role checking)
- `INDY_HUB_DISCORD_NOTIFICATION_ROLES` in settings (enables filtering)

## Usage Examples

### Example 1: Single Role

```python
# Only Industry Team members get notifications
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": True,
    },
}
```

### Example 2: Multiple Roles

```python
# Users with ANY of these roles get notifications (OR logic)
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1111111111111111111": {"name": "Industry Team", "enabled": True},
    "2222222222222222222": {"name": "Leadership", "enabled": True},
    "3333333333333333333": {"name": "Manufacturers", "enabled": True},
}
```

### Example 3: Temporarily Disable a Role

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": False,  # Temporarily disabled
    },
}
```

### Example 4: Disable Filtering

```python
# Option 1: Don't define the setting (all users notified)

# Option 2: Empty dict (all users notified)
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {}
```

## Troubleshooting

### Quick Checks

```bash
# List configured roles
python manage.py manage_discord_notification_roles list

# Test your setup
python test_discord_roles.py

# Test a specific user
python test_discord_roles.py username

# Check logs
docker logs allianceauth_worker | grep discord_roles
```

### Common Issues

| Issue | Solution |
|-------|----------|
| No roles showing in list | Add roles with management command |
| Users not filtered | Check `DISCORD_GUILD_ID` is set |
| Bot errors | Ensure Discord bot is running |
| User not linked | User must link Discord in AA |
| Role ID wrong | Must be exact 18-19 digit number |

### Enable Debug Logging

Add to `local.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'indy_hub.utils.discord_roles': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## FAQ

### Q: Do I need to restart after adding a role?

**A:** Yes, restart services after modifying `local.py`:

```bash
docker compose restart  # Docker
systemctl restart allianceauth-*  # Systemd
```

### Q: What happens if Discord bot is down?

**A:** All notifications are sent (fail-safe behavior). Check logs for warnings.

### Q: Can I use multiple roles?

**A:** Yes! Users with **any** configured role will receive notifications (OR logic).

### Q: What if a user doesn't have Discord linked?

**A:** They won't receive notifications if role filtering is enabled. They should link Discord in Alliance Auth.

### Q: How do I disable role filtering?

**A:** Remove or comment out `INDY_HUB_DISCORD_NOTIFICATION_ROLES` from `local.py`, or set it to `{}`.

### Q: Does this affect in-app notifications?

**A:** No, this only affects Discord notifications. In-app Alliance Auth notifications are not filtered.

### Q: Can I test without affecting users?

**A:** Yes, use the test script:
```bash
python test_discord_roles.py your_username
```

### Q: How do I find my Discord Guild ID?

**A:** Enable Developer Mode in Discord, right-click your server icon, Copy ID.

### Q: What if role IDs are wrong?

**A:** Use the management command to list and remove incorrect IDs:
```bash
python manage.py manage_discord_notification_roles list
python manage.py manage_discord_notification_roles remove --role-id <BAD_ID>
```

### Q: Does this work with aa-discordnotify?

**A:** Yes! It works with both `aa-discordbot` and `aa-discordnotify`.

### Q: How do I add multiple roles at once?

**A:** Run the `add` command multiple times, or manually edit `local.py`.

### Q: Can I set per-notification-type role requirements?

**A:** Not currently. All notifications use the same role requirements.

## Pattern Inspiration

This implementation follows these patterns from [BlackhawkGT/auth-scripts](https://github.com/BlackhawkGT/auth-scripts):

1. ✅ Django management commands for configuration
2. ✅ Settings-based configuration (no database)
3. ✅ Volume mount approach for Docker
4. ✅ Defensive error handling (fail-safe)
5. ✅ Clear, multi-level documentation
6. ✅ User-friendly CLI output with emojis
7. ✅ Test scripts for validation
8. ✅ Example configuration files

## Support

- 📚 Read [DISCORD_ROLES_SETUP.md](DISCORD_ROLES_SETUP.md) for detailed docs
- 🧪 Run `python test_discord_roles.py` to test your setup
- 🔍 Check logs for errors: `docker logs allianceauth_worker`
- 💬 Ask in your Alliance Auth support channels

## Credits

- **Pattern inspiration**: [BlackhawkGT/auth-scripts](https://github.com/BlackhawkGT/auth-scripts)
- **Alliance Auth**: https://allianceauth.org
- **aa-discordbot**: https://github.com/pvyParts/allianceauth-discordbot

---

**Made with ❤️ for the Alliance Auth community**
