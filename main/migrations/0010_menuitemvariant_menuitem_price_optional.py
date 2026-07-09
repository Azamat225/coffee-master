import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_fix_address_street'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Для десертов и позиций с одной ценой. Для напитков с объёмами оставьте пустым.',
                max_digits=8,
                null=True,
                verbose_name='Цена',
            ),
        ),
        migrations.CreateModel(
            name='MenuItemVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume_ml', models.PositiveIntegerField(blank=True, null=True, verbose_name='Объём, мл')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Цена')),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Цена со скидкой')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='main.menuitem', verbose_name='Позиция')),
            ],
            options={
                'verbose_name': 'Объём и цена',
                'verbose_name_plural': 'Объёмы и цены',
                'ordering': ['order', 'volume_ml', 'pk'],
            },
        ),
    ]
