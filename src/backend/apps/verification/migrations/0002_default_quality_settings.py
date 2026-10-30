from django.db import migrations


def create_default_settings(apps, schema_editor):
    """Version 1 of the quality settings with the defaults from requirements, section 4."""
    QualitySettings = apps.get_model("verification", "QualitySettings")
    if not QualitySettings.objects.exists():
        QualitySettings.objects.create(version=1, is_active=True)


def remove_default_settings(apps, schema_editor):
    QualitySettings = apps.get_model("verification", "QualitySettings")
    QualitySettings.objects.filter(version=1, reviews__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("verification", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_settings, remove_default_settings),
    ]
