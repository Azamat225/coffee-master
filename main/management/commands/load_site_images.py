import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from main.models import MosaicPhoto, SiteImage

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / 'static' / 'images' / 'gallery'
COLLAGE_DIR = STATIC_DIR / 'collage'

MOSAIC_ITEMS = [
    (1, 'collage-03.png', 'Зал студии'),
    (2, 'collage-01.png', 'Авторский напиток'),
    (3, 'collage-02.png', 'Кофе и десерты'),
    (4, 'collage-05.png', 'Интерьер'),
    (5, 'collage-04.png', 'Десерт и напиток'),
]

SITE_IMAGES = [
    ('hero', 'hero.png', 'Green Studio — атмосфера студии'),
    ('about', 'hero.png', 'О студии'),
]


class Command(BaseCommand):
    help = 'Загружает изображения страниц и коллажа в админку'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Перезаписать существующие изображения',
        )

    def handle(self, *args, **options):
        force = options['force']
        self._load_site_images(force)
        self._load_mosaic(force)
        self.stdout.write(self.style.SUCCESS('Изображения загружены.'))

    def _load_site_images(self, force):
        for key, filename, alt in SITE_IMAGES:
            if SiteImage.objects.filter(key=key).exists() and not force:
                self.stdout.write(f'  ~ {key} уже есть')
                continue

            src = STATIC_DIR / filename
            if not src.exists():
                self.stderr.write(f'  ! Не найден файл: {src}')
                continue

            obj, _ = SiteImage.objects.update_or_create(
                key=key,
                defaults={'alt_text': alt},
            )
            with open(src, 'rb') as f:
                obj.image.save(filename, File(f), save=True)
            self.stdout.write(self.style.SUCCESS(f'  + {obj.get_key_display()}'))

    def _load_mosaic(self, force):
        for order, filename, alt in MOSAIC_ITEMS:
            if MosaicPhoto.objects.filter(order=order).exists() and not force:
                self.stdout.write(f'  ~ Коллаж #{order} уже есть')
                continue

            src = COLLAGE_DIR / filename
            if not src.exists():
                self.stderr.write(f'  ! Не найден файл: {src}')
                continue

            obj, _ = MosaicPhoto.objects.update_or_create(
                order=order,
                defaults={'alt_text': alt, 'is_active': True},
            )
            with open(src, 'rb') as f:
                obj.image.save(filename, File(f), save=True)
            self.stdout.write(self.style.SUCCESS(f'  + Коллаж — порядок {order}'))
