from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0011_mosaicphoto_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkPriceAdjustment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('increase', 'Поднять'), ('decrease', 'Снизить')], max_length=10, verbose_name='Действие')),
                ('percent', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Процент')),
                ('items_count', models.PositiveIntegerField(default=0, verbose_name='Позиций')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Применено')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bulk_price_adjustments', to='main.category', verbose_name='Категория')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Кто применил')),
            ],
            options={
                'verbose_name': 'Массовое изменение цен',
                'verbose_name_plural': 'Массовые изменения цен',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BulkPriceSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Было: цена')),
                ('old_sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='Было: цена со скидкой')),
                ('adjustment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='main.bulkpriceadjustment', verbose_name='Изменение')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_snapshots', to='main.menuitem', verbose_name='Позиция')),
                ('variant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='price_snapshots', to='main.menuitemvariant', verbose_name='Объём')),
            ],
            options={
                'verbose_name': 'Снимок цены',
                'verbose_name_plural': 'Снимки цен',
                'ordering': ['menu_item_id', 'variant_id'],
            },
        ),
    ]
