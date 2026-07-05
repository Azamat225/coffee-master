from django.core.management.base import BaseCommand
from django.utils.text import slugify

from main.models import MenuItem, MenuTag

TAGS = [
    'эспрессо', 'латте', 'капучино', 'раф', 'флэт уайт', 'американо', 'макиато',
    'колд брю', 'айс кофе', 'без кофеина', 'овсяное молоко', 'миндальное молоко',
    'растительное молоко', 'декаф', 'со льдом', 'горячий', 'сливки', 'карамель',
    'ваниль', 'шоколад', 'фисташка', 'корица', 'мёд', 'сироп', 'авторский',
    'сезонный', 'хит продаж', 'веган', 'без сахара', 'низкокалорийный', 'десерт',
    'выпечка', 'торт', 'пирожное', 'макарон', 'вафля', 'круассан', 'чизкейк',
    'брауни', 'безе', 'орехи', 'ягоды', 'фрукты', 'свежее', 'домашнее', 'полдник',
    'завтрак', 'перекус', 'к столу', 'на вынос', 'матча',
]

ITEM_TAGS = {
    'Айс макиато': [
        'айс кофе', 'макиато', 'эспрессо', 'со льдом', 'хит продаж', 'полдник',
    ],
    'Айс латте': [
        'айс кофе', 'латте', 'со льдом', 'хит продаж', 'сливки', 'на вынос',
    ],
    'Макароны': [
        'макарон', 'десерт', 'фисташка', 'ваниль', 'карамель', 'хит продаж', 'полдник',
    ],
    'Тарт с безе': [
        'десерт', 'безе', 'орехи', 'домашнее', 'пирожное', 'к столу',
    ],
    'Вафля с шоколадом': [
        'вафля', 'шоколад', 'орехи', 'десерт', 'горячий', 'хит продаж', 'завтрак',
    ],
}


class Command(BaseCommand):
    help = 'Создаёт ~50 тегов меню и привязывает к позициям'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пересоздать теги (удалить старые)',
        )

    def handle(self, *args, **options):
        if options['force']:
            MenuTag.objects.all().delete()
            self.stdout.write('Старые теги удалены.')

        created = 0
        for name in TAGS:
            slug = slugify(name, allow_unicode=True) or f'tag-{created}'
            _, was_created = MenuTag.objects.get_or_create(
                slug=slug,
                defaults={'name': name},
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Тегов в базе: {MenuTag.objects.count()} (новых: {created})'))

        tag_map = {t.name: t for t in MenuTag.objects.all()}
        for item_name, tag_names in ITEM_TAGS.items():
            item = MenuItem.objects.filter(name=item_name).first()
            if not item:
                continue
            tags = [tag_map[n] for n in tag_names if n in tag_map]
            item.tags.set(tags)
            self.stdout.write(f'  {item_name}: {len(tags)} тегов')

        self.stdout.write(self.style.SUCCESS('Теги назначены.'))
