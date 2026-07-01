from django.contrib import admin
from django.utils.html import format_html

from .models import Booking, Category, GallerySlide, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'items_count')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    @admin.display(description='Позиций')
    def items_count(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'emoji_preview',
        'name',
        'category',
        'price',
        'is_popular',
        'is_available',
    )
    list_filter = ('category', 'is_popular', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_popular', 'is_available')

    @admin.display(description='')
    def emoji_preview(self, obj):
        return format_html('<span style="font-size:1.4rem">{}</span>', obj.image_emoji)


@admin.register(GallerySlide)
class GallerySlideAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    ordering = ('order', '-created_at')

    @admin.display(description='Превью')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:90px;object-fit:cover;border-radius:4px">',
                obj.image.url,
            )
        return '—'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'phone',
        'date',
        'time',
        'guests',
        'status',
        'status_badge',
        'created_at',
    )
    list_filter = ('status', 'date')
    search_fields = ('name', 'phone', 'email')
    list_editable = ('status',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)

    @admin.display(description='Статус')
    def status_badge(self, obj):
        colors = {
            'pending': '#C4A35A',
            'confirmed': '#4CAF50',
            'cancelled': '#9E9E9E',
        }
        color = colors.get(obj.status, '#888')
        label = obj.get_status_display()
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:12px">{}</span>',
            color,
            label,
        )
