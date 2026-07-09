from decimal import Decimal, ROUND_HALF_UP

from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField('Название', max_length=120, default='Green Studio Кофейня')
    topbar_text = models.CharField(
        'Текст в шапке',
        max_length=220,
        default='Кофе, уют и тишина — добро пожаловать в Green Studio Кофейня',
    )
    phone = models.CharField('Телефон', max_length=30, default='+7 905 000 64 17')
    address_name = models.CharField('Название в футере', max_length=100, default='Green Studio Кофейня')
    address_street = models.CharField('Адрес', max_length=200, default='ул. Артема 151')
    hours_weekday = models.CharField('Будни', max_length=80, default='Пн – Пт: 9:00 – 21:00')
    hours_weekend = models.CharField('Выходные', max_length=80, default='Сб – Вс: 10:00 – 20:00')
    footer_tagline = models.CharField('Слоган футера', max_length=120, default='С любовью на Артема 151')
    hero_tagline = models.CharField('Тег на главном экране', max_length=120, default='С любовью на Артема 151')
    hero_title_line1 = models.CharField('Заголовок hero, строка 1', max_length=80, default='Место, где')
    hero_title_line2 = models.CharField('Заголовок hero, строка 2', max_length=80, default='всё продумано')
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def phone_href(self):
        digits = ''.join(c for c in self.phone if c.isdigit())
        if digits.startswith('8'):
            digits = '7' + digits[1:]
        return f'+{digits}'


class Category(models.Model):
    name = models.CharField('Категория', max_length=100)
    slug = models.SlugField('URL', unique=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuTag(models.Model):
    name = models.CharField('Тег', max_length=60, unique=True)
    slug = models.SlugField('Slug', max_length=60, unique=True)

    class Meta:
        verbose_name = 'Тег меню'
        verbose_name_plural = 'Теги меню'
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Категория',
    )
    name = models.CharField('Название', max_length=150)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(
        'Цена со скидкой',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Фиксированная цена со скидкой. Если пусто — считается из акции.',
    )
    image = models.ImageField('Фото', upload_to='menu/', blank=True)
    image_emoji = models.CharField('Эмодзи', max_length=10, default='☕', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_popular = models.BooleanField('Популярное', default=False)
    is_available = models.BooleanField('В наличии', default=True)
    tags = models.ManyToManyField(MenuTag, blank=True, related_name='items', verbose_name='Теги')

    class Meta:
        verbose_name = 'Позиция меню'
        verbose_name_plural = 'Меню'
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return self.name

    def get_active_promotion(self):
        return self.promotions.filter(is_active=True).order_by('order').first()

    def get_effective_price(self):
        if self.sale_price is not None:
            return self.sale_price
        promo = self.get_active_promotion()
        if promo and promo.discount_percent:
            discounted = self.price * (1 - promo.discount_percent / Decimal('100'))
            return discounted.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        return self.price

    @property
    def has_discount(self):
        return self.get_effective_price() < self.price

    @property
    def discount_label(self):
        promo = self.get_active_promotion()
        if promo:
            return promo.title
        return 'Скидка'


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
    ]

    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True)
    date = models.DateField('Дата')
    time = models.TimeField('Время')
    guests = models.PositiveIntegerField('Гостей', default=2)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-date', '-time']

    def __str__(self):
        return f'{self.name} — {self.date} {self.time}'


class GallerySlide(models.Model):
    ASPECT_RATIO_CHOICES = [
        ('auto', 'Авто'),
        ('1:1', '1:1'),
        ('4:3', '4:3'),
        ('16:9', '16:9'),
        ('3:4', '3:4'),
    ]

    title = models.CharField('Подпись', max_length=200, blank=True)
    image = models.ImageField('Фото', upload_to='gallery/')
    aspect_ratio = models.CharField(
        'Формат',
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        default='auto',
        help_text='Авто — показывать в исходных пропорциях.',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)
    created_at = models.DateTimeField('Загружено', auto_now_add=True)

    class Meta:
        verbose_name = 'Фото галереи'
        verbose_name_plural = 'Галерея'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f'Фото #{self.pk}'


class Promotion(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст', blank=True)
    image = models.ImageField('Фото', upload_to='promotions/', blank=True)
    discount_percent = models.DecimalField(
        'Скидка, %',
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text='Скидка для привязанных позиций меню.',
    )
    menu_items = models.ManyToManyField(
        MenuItem,
        blank=True,
        related_name='promotions',
        verbose_name='Позиции меню',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class SiteImage(models.Model):
    KEY_CHOICES = [
        ('hero', 'Главная — фон'),
        ('about', 'О студии — фон'),
    ]

    key = models.CharField('Раздел', max_length=20, choices=KEY_CHOICES, unique=True)
    image = models.ImageField('Изображение', upload_to='site/')
    alt_text = models.CharField('Alt-текст', max_length=200, blank=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Изображение страницы'
        verbose_name_plural = 'Изображения страниц'

    def __str__(self):
        return self.get_key_display()


class MosaicPhoto(models.Model):
    ASPECT_RATIO_CHOICES = GallerySlide.ASPECT_RATIO_CHOICES

    SLOT_CHOICES = [
        (1, '1 — большая слева'),
        (2, '2 — широкая справа сверху'),
        (3, '3 — маленькая по центру'),
        (4, '4 — широкая снизу'),
        (5, '5 — высокая справа'),
    ]

    slot = models.PositiveSmallIntegerField('Ячейка', choices=SLOT_CHOICES, unique=True)
    image = models.ImageField('Фото', upload_to='mosaic/')
    aspect_ratio = models.CharField(
        'Формат',
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        default='auto',
        help_text='Авто — показывать в исходных пропорциях.',
    )
    alt_text = models.CharField('Подпись', max_length=200, blank=True)
    is_active = models.BooleanField('Показывать', default=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Фото коллажа'
        verbose_name_plural = 'Коллаж «Наше пространство»'
        ordering = ['slot']

    def __str__(self):
        return f'Ячейка {self.slot}' + (f' — {self.alt_text}' if self.alt_text else '')
