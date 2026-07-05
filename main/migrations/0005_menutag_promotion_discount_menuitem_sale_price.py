from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_siteimage_mosaicphoto'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True, verbose_name='Тег')),
                ('slug', models.SlugField(max_length=60, unique=True, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Тег меню',
                'verbose_name_plural': 'Теги меню',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='menuitem',
            name='sale_price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Фиксированная цена со скидкой. Если пусто — считается из акции.',
                max_digits=8,
                null=True,
                verbose_name='Цена со скидкой',
            ),
        ),
        migrations.AddField(
            model_name='promotion',
            name='discount_percent',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0'),
                help_text='Скидка в процентах для позиций, привязанных к акции.',
                max_digits=5,
                verbose_name='Скидка, %',
            ),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='items', to='main.menutag', verbose_name='Теги'),
        ),
        migrations.AddField(
            model_name='promotion',
            name='menu_items',
            field=models.ManyToManyField(blank=True, related_name='promotions', to='main.menuitem', verbose_name='Позиции меню'),
        ),
    ]
