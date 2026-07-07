from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_sitesettings_alter_promotion_discount_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryslide',
            name='aspect_ratio',
            field=models.CharField(
                choices=[
                    ('auto', 'Авто'),
                    ('1:1', '1:1'),
                    ('4:3', '4:3'),
                    ('16:9', '16:9'),
                    ('3:4', '3:4'),
                ],
                default='auto',
                help_text='Авто — показывать в исходных пропорциях.',
                max_length=10,
                verbose_name='Формат',
            ),
        ),
        migrations.AddField(
            model_name='mosaicphoto',
            name='aspect_ratio',
            field=models.CharField(
                choices=[
                    ('auto', 'Авто'),
                    ('1:1', '1:1'),
                    ('4:3', '4:3'),
                    ('16:9', '16:9'),
                    ('3:4', '3:4'),
                ],
                default='auto',
                help_text='Авто — показывать в исходных пропорциях.',
                max_length=10,
                verbose_name='Формат',
            ),
        ),
    ]
