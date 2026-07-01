from django.db import models


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
    image_emoji = models.CharField('Эмодзи', max_length=10, default='☕')
    is_popular = models.BooleanField('Популярное', default=False)
    is_available = models.BooleanField('В наличии', default=True)

    class Meta:
        verbose_name = 'Позиция меню'
        verbose_name_plural = 'Меню'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


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
    title = models.CharField('Подпись', max_length=200, blank=True)
    image = models.ImageField('Фото', upload_to='gallery/')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)
    created_at = models.DateTimeField('Загружено', auto_now_add=True)

    class Meta:
        verbose_name = 'Фото галереи'
        verbose_name_plural = 'Галерея'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f'Фото #{self.pk}'
