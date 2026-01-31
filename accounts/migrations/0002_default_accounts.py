from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_default_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")

    defaults = [
        {
            "username": "admin",
            "password": "12345",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "username": "user",
            "password": "12345",
            "role": "user",
            "is_staff": True,
            "is_superuser": False,
        },
    ]

    for entry in defaults:
        user, created = User.objects.get_or_create(username=entry["username"])
        user.role = entry["role"]
        user.is_staff = entry["is_staff"]
        user.is_superuser = entry["is_superuser"]
        user.is_active = True
        user.password = make_password(entry["password"])  # <<< Encripta
        user.save()


def remove_default_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(username__in=["admin", "user"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_users, remove_default_users),
    ]
