from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_promotion_alter_menuitem_options_menuitem_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('hero', 'Главная — фон'), ('about', 'О студии — фон')], max_length=20, unique=True, verbose_name='Раздел')),
                ('image', models.ImageField(upload_to='site/', verbose_name='Изображение')),
                ('alt_text', models.CharField(blank=True, max_length=200, verbose_name='Alt-текст')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Изображение страницы',
                'verbose_name_plural': 'Изображения страниц',
            },
        ),
        migrations.CreateModel(
            name='MosaicPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.PositiveSmallIntegerField(choices=[(1, '1 — большая слева'), (2, '2 — широкая справа сверху'), (3, '3 — маленькая по центру'), (4, '4 — широкая снизу'), (5, '5 — высокая справа')], unique=True, verbose_name='Ячейка')),
                ('image', models.ImageField(upload_to='mosaic/', verbose_name='Фото')),
                ('alt_text', models.CharField(blank=True, max_length=200, verbose_name='Подпись')),
                ('is_active', models.BooleanField(default=True, verbose_name='Показывать')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Фото коллажа',
                'verbose_name_plural': 'Коллаж «Наше пространство»',
                'ordering': ['slot'],
            },
        ),
    ]
