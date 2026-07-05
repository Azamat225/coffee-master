from decimal import Decimal

import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from main.models import Category, MenuItem, Promotion

ASSETS = Path(
    r'C:\Users\bikme\.cursor\projects\c-Users-bikme-Downloads-coffee-master-coffee-master\assets'
)

MENU_IMAGES = {
    'ice-macchiato.png': 'c__Users_bikme_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_image-d48d4898-21d6-4ed3-95ee-7e58b55f88e9.png',
    'ice-latte.png': 'c__Users_bikme_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_image-96816bd8-b6c4-4eca-ae83-ef400090e42a.png',
    'macarons.png': 'c__Users_bikme_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_image-9b2cbadf-bc7b-4887-b6cf-451049726426.png',
    'meringue-tart.png': 'c__Users_bikme_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_image-24ceecbe-7cbf-4d6b-89a0-efd72d9932d7.png',
    'waffle.png': 'c__Users_bikme_AppData_Roaming_Cursor_User_workspaceStorage_empty-window_images_image-8bd7d406-cc90-4c2c-bcc7-6ca7028804e9.png',
}

MENU = [
    {
        'category': ('Напитки', 'drinks', 1),
        'items': [
            ('Айс макиато', 'Слои эспрессо и молока со льдом', 290, 'ice-macchiato.png', 1, True),
            ('Айс латте', 'Нежный холодный латте с молоком', 280, 'ice-latte.png', 2, True),
        ],
    },
    {
        'category': ('Десерты', 'desserts', 2),
        'items': [
            ('Макароны', 'Три макарона: ваниль, фисташка, карамель', 320, 'macarons.png', 1, True),
            ('Тарт с безе', 'Хрустящая основа, безе и орехи', 360, 'meringue-tart.png', 2, False),
            ('Вафля с шоколадом', 'Свежая вафля, шоколад и орехи', 340, 'waffle.png', 3, True),
        ],
    },
]


class Command(BaseCommand):
    help = 'Загружает меню с фото из скриншотов'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Перезаписать существующее меню')

    def handle(self, *args, **options):
        if MenuItem.objects.exists() and not options['force']:
            self.stdout.write('Меню уже есть — используйте --force для перезаписи.')
            return

        if options['force']:
            MenuItem.objects.all().delete()
            Category.objects.all().delete()

        menu_dir = Path(settings.MEDIA_ROOT) / 'menu'
        menu_dir.mkdir(parents=True, exist_ok=True)

        for cat_data in MENU:
            cat_name, cat_slug, cat_order = cat_data['category']
            category, _ = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={'name': cat_name, 'order': cat_order},
            )

            for name, desc, price, img_file, order, popular in cat_data['items']:
                src_name = MENU_IMAGES.get(img_file)
                src_path = ASSETS / src_name if src_name else None
                dest_path = menu_dir / img_file

                if src_path and src_path.exists():
                    shutil.copy2(src_path, dest_path)

                item = MenuItem(
                    category=category,
                    name=name,
                    description=desc,
                    price=price,
                    order=order,
                    is_popular=popular,
                )
                if dest_path.exists():
                    with open(dest_path, 'rb') as f:
                        item.image.save(img_file, File(f), save=False)
                item.save()
                self.stdout.write(self.style.SUCCESS(f'  + {name}'))

        if not Promotion.objects.exists():
            promo_dir = Path(settings.MEDIA_ROOT) / 'promotions'
            promo_dir.mkdir(parents=True, exist_ok=True)
            src = ASSETS / MENU_IMAGES['macarons.png']
            if src.exists():
                promo = Promotion(
                    title='Кофе и десерт',
                    text='Айс латте и макароны — идеальное сочетание для полдника',
                    discount_percent=Decimal('15'),
                    order=0,
                    is_active=True,
                )
                with open(src, 'rb') as f:
                    promo.image.save('promo-coffee-dessert.png', File(f), save=True)
                latte = MenuItem.objects.filter(name='Айс латте').first()
                macarons = MenuItem.objects.filter(name='Макароны').first()
                if latte:
                    promo.menu_items.add(latte)
                if macarons:
                    promo.menu_items.add(macarons)
                self.stdout.write(self.style.SUCCESS('  + пример акции (15% на латте и макароны)'))

        self.stdout.write(self.style.SUCCESS('Меню загружено. Запустите: python manage.py load_menu_tags'))
