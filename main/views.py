from django.http import HttpResponse
from django.shortcuts import render

from .models import GallerySlide, MenuItem, MosaicPhoto, Promotion, SiteImage


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


def _build_gallery_items():
    items = []
    for photo in MosaicPhoto.objects.filter(is_active=True).order_by('slot'):
        items.append({
            'image': photo.image,
            'title': photo.alt_text,
            'aspect_ratio': photo.aspect_ratio,
            'sort': photo.slot,
        })
    for slide in GallerySlide.objects.filter(is_active=True).order_by('order', '-created_at'):
        items.append({
            'image': slide.image,
            'title': slide.title,
            'aspect_ratio': slide.aspect_ratio,
            'sort': 100 + slide.order,
        })
    items.sort(key=lambda item: item['sort'])
    return items


def home(request):
    return render(request, 'main/home.html', {
        'site_images': _site_images(),
        'popular_items': (
            MenuItem.objects.filter(is_available=True, is_popular=True)
            .prefetch_related('tags', 'promotions')[:4]
        ),
    })


def menu_page(request):
    menu_items = (
        MenuItem.objects.filter(is_available=True)
        .prefetch_related('tags', 'promotions')
        .order_by('category__order', 'order', 'name')
    )
    return render(request, 'main/menu.html', {'menu_items': menu_items})


def promotions_page(request):
    promotions = Promotion.objects.filter(is_active=True).prefetch_related('menu_items')
    return render(request, 'main/promotions.html', {'promotions': promotions})


def gallery_page(request):
    return render(request, 'main/gallery.html', {
        'gallery_items': _build_gallery_items(),
    })


def contacts_page(request):
    return render(request, 'main/contacts.html')
