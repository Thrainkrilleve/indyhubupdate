# Discord Role-Based Notifications - Quick Start

## 🎯 Goal
Only notify users with specific Discord roles (like "Industry Team" or "Leadership") instead of everyone.

## ⚡ Quick Setup (5 Minutes)

### 1. Get Your Discord Role ID

In Discord:
1. Settings → Advanced → Turn on "Developer Mode"
2. Right-click your role (e.g., "Industry Team") → Copy ID
3. Save the ID (example: `1234567890123456789`)

### 2. Add the Role

```bash
python manage.py manage_discord_notification_roles add \
    --role-id 1234567890123456789 \
    --role-name "Industry Team"
```

### 3. Copy the Settings

The command will show you settings to add. Copy them to your `local.py`:

```python
INDY_HUB_DISCORD_NOTIFICATION_ROLES = {
    "1234567890123456789": {
        "name": "Industry Team",
        "enabled": True,
    },
}

# Also required for role checking
DISCORD_GUILD_ID = 123456789012345678  # Your Discord server ID
```

### 4. Restart

```bash
# Docker
docker compose restart

# Systemd
systemctl restart allianceauth-*
```

## ✅ Done!

Now only users with the "Industry Team" role get notifications.

## 📚 More Details

See [DISCORD_ROLES_SETUP.md](DISCORD_ROLES_SETUP.md) for:
- Multiple roles
- Testing
- Troubleshooting
- Advanced configuration

## 🔧 Quick Commands

```bash
# List configured roles
python manage.py manage_discord_notification_roles list

# Add a role
python manage.py manage_discord_notification_roles add --role-id <ID> --role-name "Name"

# Remove a role
python manage.py manage_discord_notification_roles remove --role-id <ID>

# Remove all (notify everyone again)
python manage.py manage_discord_notification_roles clear
```

## 💡 Tips

- **Multiple roles?** Run the `add` command multiple times
- **No filtering?** Don't add `INDY_HUB_DISCORD_NOTIFICATION_ROLES` to settings
- **Testing?** Set `enabled: False` for a role temporarily
- **Troubleshooting?** Check logs: `docker logs allianceauth_worker | grep discord_roles`

## Pattern Credit

Based on [BlackhawkGT/auth-scripts](https://github.com/BlackhawkGT/auth-scripts) patterns for Alliance Auth customizations.
