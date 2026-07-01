import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from main.models import GallerySlide

FALLBACK_DIR = Path(__file__).resolve().parent.parent.parent / 'static' / 'images' / 'gallery'

SLIDES = [
    ('slide-01.png', 'Интерьер студии'),
    ('slide-02.png', 'Зона отдыха'),
    ('slide-03.png', 'Пространство для встреч'),
    ('slide-04.png', 'Детали интерьера'),
    ('slide-05.png', 'Кофейная станция'),
    ('slide-06.png', 'Атмосфера'),
]


class Command(BaseCommand):
    help = 'Загружает начальные фото в галерею'

    def handle(self, *args, **options):
        if GallerySlide.objects.exists():
            self.stdout.write('Галерея уже заполнена — пропуск.')
            return

        source_dir = FALLBACK_DIR
        if not source_dir.exists():
            self.stderr.write(f'Папка с фото не найдена: {source_dir}')
            return

        images = sorted(source_dir.glob('*.png'))
        if not images:
            self.stderr.write('PNG-файлы не найдены.')
            return

        gallery_dir = Path(settings.MEDIA_ROOT) / 'gallery'
        gallery_dir.mkdir(parents=True, exist_ok=True)

        for i, (img_path, (_, title)) in enumerate(zip(images, SLIDES)):
            dest_name = f'slide-{i + 1:02d}.png'
            dest_path = gallery_dir / dest_name
            shutil.copy2(img_path, dest_path)

            slide = GallerySlide(title=title, order=i, is_active=True)
            with open(dest_path, 'rb') as f:
                slide.image.save(dest_name, File(f), save=True)

            self.stdout.write(self.style.SUCCESS(f'  + {title}'))

        self.stdout.write(self.style.SUCCESS(f'Загружено {len(images)} фото.'))
