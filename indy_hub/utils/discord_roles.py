"""
Utilities for filtering Discord notifications by role
Following BlackhawkGT/auth-scripts pattern for Discord integrations

Supports separate role configurations for:
- Industry notifications (blueprints, jobs, copy requests)
- Material Exchange admin notifications (new orders to review)
- User-specific notifications (always sent, no filtering)
"""

# Standard Library
import logging

# Django
from django.conf import settings

logger = logging.getLogger(__name__)


# Notification type constants
NOTIFICATION_TYPE_INDUSTRY = "industry"
NOTIFICATION_TYPE_MATERIAL_EXCHANGE = "material_exchange"
NOTIFICATION_TYPE_USER = "user"

notification_type=NOTIFICATION_TYPE_INDUSTRY):
    """
    Check if role-based notification filtering is enabled for a type.
    
    Args:
        notification_type: Type of notification to check
        
    Returns:
        bool: True if role filtering is configured and enabled
    """
    roles = get_notification_roles(notification_type)
    if not roles:
        return False
    
    # At least one role must be enabled
    return any(role.get("enabled", True) for role in roles.values())


def get_enabled_role_ids(notification_type=NOTIFICATION_TYPE_INDUSTRY):
    """
    Get list of enabled Discord role IDs for a notification type.
    
    Args:
        notification_type: Type of notification
        
    Returns:
        list: List of Discord role IDs as strings
    """
    roles = get_notification_roles(notification_typen filtering is enabled.
    
    Returns:
        bool: True if role filtering is configured and enabled
    """
    roles = get_notification_roles()
    if not roles:
        return False
    
    # At least one role must be enabled
    return any(role.get("enabled", True) for role in roles.values())


def get_enabled_role_ids():
    """
    Get list of enabled Discord role IDs for notifications.
    
    Returns:
        list: List of Discord role IDs as strings
    """
    roles = get_notification_roles()
    return [
        role_id , notification_type=NOTIFICATION_TYPE_INDUSTRY):
    """
    Check if a user has a Discord role for a specific notification type.
    
    Args:
        user: Django User object
        notification_type: Type of notification (industry, material_exchange, user)
        
    Returns:
        bool: True if user should receive notifications based on roles,
              or if role filtering is disabled (all users get notifications)
    """
    # User-specific notifications always go through (no filtering)
    if notification_type == NOTIFICATION_TYPE_USER:
        return True
    
    # If no role filtering configured for this type, allow all notifications
    if not is_notification_enabled(notification_type
    Returns:
        bool: True if user should receive notifications based on roles,
              or if role filtering is disabled (all users get notifications)
    """
    # If no role filtering configured, allow all notifications
    if not is_notification_enabled():
        return True
    
    try:
        # Check if aadiscordbot is available
        from django.apps import apps
        if not apps.is_installed("aadiscordbot"):
            logger.debug("aadiscordbot not installed, allowing all notifications")
            return True
        
        # Try to get user's Discord account
        discord_user = getattr(user, "discord", None)
        if not discord_user:
            logger.debug(f"User {user.username} has no Discord account linked")
            return False
        
        # Get the user's Discord member object
        try:
            from aadiscordbot.models import DiscordUser
            discord_account = DiscordUser.objects.filter(user=user).first()
            
            if not discord_account:
                logger.debug(f"User {user.username} has no Discord account in database")
                return False
            
            # Check if we can get member roles via Discord API
            # This requires aadiscordbot to be properly configured
            from discord.utils import get as discord_get
            from aadiscordbot.app_settings import get_bot
            
            bot = get_bot()
            if not bot:
                logger.debug("Discord bot not available, allowing all notifications")
                return True
            
            guild_id = getattr(settings, "DISCORD_GUILD_ID", None)
            if not guild_id:
                logger.debug("DISCORD_GUILD_ID not configured, allowing all notifications")
                return True
             for this notification type
            enabled_roles = get_enabled_role_ids(notification_type)
            user_role_ids = [str(role.id) for role in member.roles]
            
            has_role = any(role_id in user_role_ids for role_id in enabled_roles)
            
            if has_role:
                logger.debug(f"User {user.username} has {notification_type} notification role")
            else:
                logger.debug(f"User {user.username} does not have {notification_type}
            
            # Check if user has any of the configured roles
            enabled_roles = get_enabled_role_ids()
            user_role_ids = [str(role.id) for role in member.roles]
            
            has_role = any(role_id in user_role_ids for role_id in enabled_roles)
            
            if has_role:
                logger.debug(f"User {user.username} has notification role")
            else:
                logger.debug(f"User {user.username} does not have notification role")
            
            return has_role
            
        except ImportError:
            logger.debug("aadiscordbot not properly configured, allowing all notifications")
            return True
        except Exception as e:
            logger.warning(
                f"Error checking Discord roles for {user.username}: {e}",
                exc_info=True
            )
            # On error, allow notifications to avoid blocking users
            return True
            
    except Exception as e:
        logger.error(
            f"Unexpected error checking notification roles: {e}",
            exc_info=True, notification_type=NOTIFICATION_TYPE_INDUSTRY):
    """
    Filter a list of users to only those with notification roles for a type.
    
    Args:
        users: QuerySet, list, or single User object
        notification_type: Type of notification (industry, material_exchange, user)
        
    Returns:
        list: Filtered list of users who should receive notifications
    """
    # Convert to list if needed
    if hasattr(users, "all"):
        users = list(users)
    elif not isinstance(users, (list, tuple)):
        users = [users]
    
    # User-specific notifications go to all users (no filtering)
    if notification_type == NOTIFICATION_TYPE_USER:
        return users
    
    # If role filtering is disabled for this type, return all users
    if not is_notification_enabled(notification_type):
        return users
    
    # Filter users by role
    filtered_users = []
    for user in users:
        if user_has_notification_role(user, notification_type):
            filtered_users.append(user)
        else:
            logger.debug(
                f"Skipping {notification_type}
        if user_has_notification_role(user):
            filtered_users.append(user)
        else:
            logger.debug(
                f"Skipping notification for {user.username} - no notification role"
            )
    
    return filtered_users
