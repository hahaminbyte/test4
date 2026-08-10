# Generated manually for wallet sign-in.

from django.db import migrations, models


class Migration(migrations.Migration):
    """Add wallet_address to TrakUser."""

    dependencies = [
        ("core", "0004_remove_role_permissions_delete_permission_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="trakuser",
            name="wallet_address",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Ethereum-compatible wallet address used for MetaMask sign-in.",
                max_length=42,
                null=True,
                unique=True,
            ),
        ),
    ]
