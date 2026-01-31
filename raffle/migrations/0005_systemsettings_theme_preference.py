from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raffle", "0004_coupon_created_by_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemsettings",
            name="theme_preference",
            field=models.CharField(
                choices=[("light", "Tema claro"), ("dark", "Tema oscuro")],
                default="light",
                max_length=10,
            ),
        ),
    ]
