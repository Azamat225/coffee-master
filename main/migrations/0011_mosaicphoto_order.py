from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_menuitemvariant_menuitem_price_optional'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mosaicphoto',
            old_name='slot',
            new_name='order',
        ),
        migrations.AlterField(
            model_name='mosaicphoto',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок'),
        ),
    ]
