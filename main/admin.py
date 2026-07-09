from django.contrib import admin
from django.utils.html import format_html

from .models import Booking, Category, GallerySlide, MenuItem, MosaicPhoto, Promotion, SiteImage


def image_preview_field(url, height=56, width=84):
    return format_html(
        '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;border-radius:4px">',
        url, height, width,
    )


@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ('key', 'image_preview', 'alt_text', 'updated_at')
    readonly_fields = ('image_preview_large', 'updated_at')
    fields = ('key', 'image', 'image_preview_large', 'alt_text', 'updated_at')

    @admin.display(description='Превью')
    def image_preview(self, obj):
        if obj.image:
            return image_preview_field(obj.image.url)
        return '—'

    @admin.display(description='Превью')
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:360px;max-height:200px;object-fit:cover;border-radius:6px">',
                obj.image.url,
            )
        return '—'


@admin.register(MosaicPhoto)
class MosaicPhotoAdmin(admin.ModelAdmin):
    list_display = ('order', 'image_preview', 'alt_text', 'is_active', 'updated_at')
    list_display_links = ('alt_text',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    ordering = ('order', 'pk')
    readonly_fields = ('image_preview_large', 'updated_at')
    fields = ('order', 'image', 'image_preview_large', 'aspect_ratio', 'alt_text', 'is_active', 'updated_at')

    @admin.display(description='Превью')
    def image_preview(self, obj):
        if obj.image:
            return image_preview_field(obj.image.url, 48, 64)
        return '—'

    @admin.display(description='Превью')
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:320px;max-height:240px;object-fit:cover;border-radius:6px">',
                obj.image.url,
            )
        return '—'


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'text')
    ordering = ('order', '-created_at')
    readonly_fields = ('image_preview_large', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'image', 'image_preview_large', 'order', 'is_active', 'created_at'),
        }),
    )

    @admin.display(description='Фото')
    def image_preview(self, obj):
        if obj.image:
            return image_preview_field(obj.image.url)
        return '—'

    @admin.display(description='Превью')
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:360px;max-height:220px;object-fit:cover;border-radius:6px">',
                obj.image.url,
            )
        return '—'


@admin.register(GallerySlide)
class GallerySlideAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    ordering = ('order', '-created_at')
    fieldsets = (
        (None, {
            'fields': ('image', 'title', 'aspect_ratio', 'order', 'is_active'),
        }),
    )

    @admin.display(description='Фото')
    def image_preview(self, obj):
        if obj.image:
            return image_preview_field(obj.image.url)
        return '—'


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ('name', 'price', 'image', 'order', 'is_popular', 'is_available')
    ordering = ('order', 'name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'items_count')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    inlines = [MenuItemInline]

    @admin.display(description='Позиций')
    def items_count(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        'image_preview',
        'name',
        'category',
        'price',
        'order',
        'is_popular',
        'is_available',
    )
    list_filter = ('category', 'is_popular', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'order', 'is_popular', 'is_available')
    ordering = ('category', 'order', 'name')
    readonly_fields = ('image_preview_large',)
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'description', 'price', 'image', 'image_preview_large', 'order'),
        }),
        ('Настройки', {
            'fields': ('is_popular', 'is_available'),
        }),
    )

    @admin.display(description='Фото')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px;width:48px;object-fit:cover;border-radius:50%">',
                obj.image.url,
            )
        return '—'

    @admin.display(description='Превью')
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:200px;max-height:200px;object-fit:cover;border-radius:6px">',
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
