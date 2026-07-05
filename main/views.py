from django.http import HttpResponse
from django.shortcuts import render

from .models import MenuItem, MosaicPhoto, Promotion, SiteImage


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Disallow: /panel/',
        'Disallow: /admin/',
        '',
        'Allow: /',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


def home(request):
    menu_items = (
        MenuItem.objects.filter(is_available=True)
        .prefetch_related('tags', 'promotions')
        .order_by('order', 'name')
    )
    promotions = Promotion.objects.filter(is_active=True)
    mosaic_photos = MosaicPhoto.objects.filter(is_active=True).order_by('slot')
    site_images = {img.key: img for img in SiteImage.objects.all()}
    return render(request, 'main/home.html', {
        'menu_items': menu_items,
        'promotions': promotions,
        'mosaic_photos': mosaic_photos,
        'site_images': site_images,
    })
