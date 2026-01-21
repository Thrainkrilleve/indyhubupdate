# Django
from django.db import migrations


def rename_asset_tables_if_needed(apps, schema_editor):
    """Rename asset tables only if old names exist (for upgrades)"""
    from django.db import connection
    with connection.cursor() as cursor:
        # Check and rename corporation assets table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'indy_hub_cachedcorporationasset'
        """)
        if cursor.fetchone()[0] > 0:
            cursor.execute("RENAME TABLE indy_hub_cachedcorporationasset TO indy_hub_corp_assets")
        
        # Check and rename character assets table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'indy_hub_cachedcharacterasset'
        """)
        if cursor.fetchone()[0] > 0:
            cursor.execute("RENAME TABLE indy_hub_cachedcharacterasset TO indy_hub_char_assets")


class Migration(migrations.Migration):

    dependencies = [
        ("indy_hub", "0069_add_material_exchange_market_group_filters"),
    ]

    operations = [
        # Run Python code to conditionally rename tables
        migrations.RunPython(rename_asset_tables_if_needed, migrations.RunPython.noop),
        # Set model table names (no-op if already renamed, creates new if fresh install)
        migrations.AlterModelTable(
            name="cachedcorporationasset",
            table="indy_hub_corp_assets",
        ),
        migrations.AlterModelTable(
            name="cachedcharacterasset",
            table="indy_hub_char_assets",
        ),
    ]
