from django.db.models import Prefetch

from django.http import HttpResponse
from django.shortcuts import render

from .models import Category, GallerySlide, MenuItem, MosaicPhoto, Promotion, SiteImage


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Disallow: /panel/',
        'Disallow: /admin/',
        '',
        'Allow: /',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


def _site_images():
    return {img.key: img for img in SiteImage.objects.all()}


def _aspect_class(ratio):
    if not ratio or ratio == 'auto':
        return ''
    return f'gallery-item--{ratio.replace(":", "-")}'


def _build_gallery_items():
    items = []
    for photo in MosaicPhoto.objects.filter(is_active=True).order_by('order', 'pk'):
        ratio = getattr(photo, 'aspect_ratio', 'auto')
        items.append({
            'image': photo.image,
            'title': photo.alt_text,
            'aspect_class': _aspect_class(ratio),
            'sort': photo.order,
        })
    for slide in GallerySlide.objects.filter(is_active=True).order_by('order', '-created_at'):
        ratio = getattr(slide, 'aspect_ratio', 'auto')
        items.append({
            'image': slide.image,
            'title': slide.title,
            'aspect_class': _aspect_class(ratio),
            'sort': 100 + slide.order,
        })
    items.sort(key=lambda item: item['sort'])
    return items


def _menu_item_queryset():
    return (
        MenuItem.objects.filter(is_available=True)
        .prefetch_related('tags', 'promotions', 'variants')
        .order_by('order', 'name')
    )


def _build_menu_categories():
    available = _menu_item_queryset()
    categories = Category.objects.prefetch_related(
        Prefetch('items', queryset=available)
    ).order_by('order', 'name')

    sections = []
    for category in categories:
        items = list(category.items.all())
        if not items:
            continue
        with_photo = [item for item in items if item.has_image]
        without_photo = [item for item in items if not item.has_image]
        sections.append({
            'category': category,
            'with_photo': with_photo,
            'without_photo': without_photo,
        })
    return sections


def home(request):
    return render(request, 'main/home.html', {
        'site_images': _site_images(),
        'popular_items': (
            MenuItem.objects.filter(is_available=True, is_popular=True)
            .prefetch_related('tags', 'promotions', 'variants')[:4]
        ),
    })


def menu_page(request):
    return render(request, 'main/menu.html', {
        'menu_categories': _build_menu_categories(),
    })


def promotions_page(request):
    promotions = Promotion.objects.filter(is_active=True).prefetch_related('menu_items')
    return render(request, 'main/promotions.html', {'promotions': promotions})


def gallery_page(request):
    return render(request, 'main/gallery.html', {
        'gallery_items': _build_gallery_items(),
    })


def contacts_page(request):
    return render(request, 'main/contacts.html')
