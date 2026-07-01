from django.core.management.base import BaseCommand

from main.models import Category, MenuItem


class Command(BaseCommand):
    help = 'Заполняет базу начальными данными меню'

    def handle(self, *args, **options):
        if Category.objects.exists():
            self.stdout.write('Данные уже существуют, пропуск.')
            return

        categories_data = [
            {
                'name': 'Кофе',
                'slug': 'coffee',
                'order': 1,
                'items': [
                    ('Эспрессо', 'Классический крепкий эспрессо из зёрен арабики', 180, '☕', True),
                    ('Капучино', 'Нежный капучино с воздушной молочной пенкой', 250, '☕', True),
                    ('Латте', 'Мягкий латте с карамельными нотками', 270, '🥛', True),
                    ('Раф ванильный', 'Авторский раф на сливках с ванилью', 320, '✨', True),
                    ('Флэт уайт', 'Двойной эспрессо с микропеной', 290, '☕', False),
                ],
            },
            {
                'name': 'Альтернатива',
                'slug': 'alt',
                'order': 2,
                'items': [
                    ('Пуровер V60', 'Фильтр-кофе ручной заварки', 300, '💧', True),
                    ('Айс латте', 'Освежающий холодный латте со льдом', 290, '🧊', False),
                    ('Матча латте', 'Японский зелёный чай с молоком', 310, '🍵', True),
                ],
            },
            {
                'name': 'Десерты',
                'slug': 'desserts',
                'order': 3,
                'items': [
                    ('Круассан', 'Свежая французская выпечка', 180, '🥐', True),
                    ('Чизкейк Нью-Йорк', 'Классический чизкейк с ягодным соусом', 350, '🍰', True),
                    ('Брауни', 'Шоколадный брауни с грецким орехом', 280, '🍫', False),
                    ('Тирамису', 'Итальянский десерт с маскарпоне', 380, '🍮', True),
                ],
            },
            {
                'name': 'Завтраки',
                'slug': 'breakfast',
                'order': 4,
                'items': [
                    ('Яичница с авокадо', 'На хлебе с зеленью и помидорами', 420, '🍳', True),
                    ('Овсянка с ягодами', 'Полезный завтрак с мёдом и орехами', 320, '🥣', False),
                    ('Сырники', 'Домашние сырники со сметаной', 360, '🧀', True),
                ],
            },
        ]

        for cat_data in categories_data:
            items = cat_data.pop('items')
            category = Category.objects.create(**cat_data)
            for name, desc, price, emoji, popular in items:
                MenuItem.objects.create(
                    category=category,
                    name=name,
                    description=desc,
                    price=price,
                    image_emoji=emoji,
                    is_popular=popular,
                )

        self.stdout.write(self.style.SUCCESS('Начальные данные успешно загружены!'))
