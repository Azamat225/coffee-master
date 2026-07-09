from django.db import migrations


def fix_address_street(apps, schema_editor):
    SiteSettings = apps.get_model('main', 'SiteSettings')
    for settings in SiteSettings.objects.all():
        street = (settings.address_street or '').strip()
        if 'этаж' in street.lower():
            settings.address_street = 'ул. Артема 151'
            settings.save(update_fields=['address_street'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_sitesettings_address_street'),
    ]

    operations = [
        migrations.RunPython(fix_address_street, migrations.RunPython.noop),
    ]
