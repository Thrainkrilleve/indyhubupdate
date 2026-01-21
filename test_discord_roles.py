"""
Test script for Discord role-based notifications
Run this to verify your setup is working correctly
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myauth.settings")
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from indy_hub.utils.discord_roles import (
    get_notification_roles,
    is_notification_enabled,
    get_enabled_role_ids,
    user_has_notification_role,
    filter_users_by_notification_role,
)


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_role_configuration():
    """Test if roles are configured"""
    print_header("Testing Role Configuration")
    
    roles = get_notification_roles()
    
    if not roles:
        print("❌ No roles configured")
        print("   Add roles in your local.py or use the management command:")
        print("   python manage.py manage_discord_notification_roles add --role-id <ID> --role-name <NAME>")
        return False
    
    print(f"✅ Found {len(roles)} configured role(s):")
    for role_id, config in roles.items():
        status = "✓ Enabled" if config.get("enabled", True) else "✗ Disabled"
        print(f"   - {config.get('name', 'Unknown')} (ID: {role_id}) [{status}]")
    
    return True


def test_notification_enabled():
    """Test if notification filtering is enabled"""
    print_header("Testing Notification Filtering Status")
    
    enabled = is_notification_enabled()
    
    if enabled:
        print("✅ Role-based notification filtering is ENABLED")
        role_ids = get_enabled_role_ids()
        print(f"   Active role IDs: {', '.join(role_ids)}")
    else:
        print("⚠️  Role-based notification filtering is DISABLED")
        print("   All users will receive notifications")
    
    return enabled


def test_discord_guild_id():
    """Test if Discord Guild ID is configured"""
    print_header("Testing Discord Guild ID")
    
    guild_id = getattr(settings, "DISCORD_GUILD_ID", None)
    
    if guild_id:
        print(f"✅ Discord Guild ID configured: {guild_id}")
        return True
    else:
        print("❌ DISCORD_GUILD_ID not configured in settings")
        print("   Add this to your local.py:")
        print("   DISCORD_GUILD_ID = 123456789012345678")
        return False


def test_discord_bot():
    """Test if Discord bot is available"""
    print_header("Testing Discord Bot Integration")
    
    from django.apps import apps
    
    if not apps.is_installed("aadiscordbot"):
        print("⚠️  aadiscordbot not installed")
        print("   Install with: pip install aa-discordbot")
        return False
    
    print("✅ aadiscordbot is installed")
    
    try:
        from aadiscordbot.app_settings import get_bot
        bot = get_bot()
        
        if bot:
            print(f"✅ Discord bot is connected")
            print(f"   Bot user: {bot.user}")
            return True
        else:
            print("⚠️  Discord bot not connected")
            print("   Make sure the Discord bot is running")
            return False
    except Exception as e:
        print(f"⚠️  Could not check bot status: {e}")
        return False


def test_user_role_check(username=None):
    """Test role check for a specific user"""
    print_header("Testing User Role Check")
    
    if not username:
        print("ℹ️  No username provided, skipping user-specific test")
        print("   Run with: python test_discord_roles.py <username>")
        return True
    
    try:
        user = User.objects.get(username=username)
        print(f"✅ Found user: {user.username}")
        
        has_role = user_has_notification_role(user)
        
        if has_role:
            print(f"✅ User {username} HAS notification role")
            print("   This user will receive notifications")
        else:
            print(f"❌ User {username} DOES NOT have notification role")
            print("   This user will NOT receive notifications")
        
        # Check Discord account
        discord_user = getattr(user, "discord", None)
        if discord_user:
            print(f"ℹ️  Discord account linked: {discord_user.uid}")
        else:
            print("⚠️  No Discord account linked for this user")
        
        return True
        
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        return False
    except Exception as e:
        print(f"❌ Error testing user: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filter_users():
    """Test filtering multiple users"""
    print_header("Testing User Filtering")
    
    users = User.objects.all()[:5]  # Test with first 5 users
    
    if not users:
        print("⚠️  No users found in database")
        return False
    
    print(f"Testing with {len(users)} users...")
    
    filtered = filter_users_by_notification_role(users)
    
    print(f"✅ Filtered from {len(users)} to {len(filtered)} users")
    
    if len(filtered) < len(users):
        print(f"   {len(users) - len(filtered)} user(s) filtered out (no notification role)")
    
    for user in filtered[:3]:  # Show first 3
        print(f"   - {user.username} (will receive notifications)")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  Discord Role-Based Notifications - Test Suite")
    print("=" * 70)
    print("\n📋 This script will test your Discord notification role setup\n")
    
    # Get username from command line if provided
    username = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run tests
    results = []
    results.append(("Role Configuration", test_role_configuration()))
    results.append(("Notification Enabled", test_notification_enabled()))
    results.append(("Discord Guild ID", test_discord_guild_id()))
    results.append(("Discord Bot", test_discord_bot()))
    results.append(("User Role Check", test_user_role_check(username)))
    results.append(("User Filtering", test_filter_users()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup looks good.")
    else:
        print("\n⚠️  Some tests failed. Review the output above for details.")
    
    # Usage tips
    print_header("Usage Tips")
    print("📝 Management commands:")
    print("   python manage.py manage_discord_notification_roles list")
    print("   python manage.py manage_discord_notification_roles add --role-id <ID> --role-name <NAME>")
    print("\n📚 Documentation:")
    print("   See DISCORD_ROLES_QUICKSTART.md for setup")
    print("   See DISCORD_ROLES_SETUP.md for full documentation")
    print("\n🔍 Test a specific user:")
    print("   python test_discord_roles.py <username>")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
