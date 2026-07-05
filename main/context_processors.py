from django.conf import settings as django_settings

from .models import MenuTag, SiteSettings


def build_seo_keywords():
    settings = SiteSettings.get_solo()
    tag_names = MenuTag.objects.order_by('name').values_list('name', flat=True)
    base_words = [
        settings.site_name,
        'кофейня',
        'десерты',
        'меню',
        settings.address_street,
    ]
    seen = set()
    keywords = []
    for word in base_words:
        key = word.lower()
        if key not in seen:
            seen.add(key)
            keywords.append(word)
    for name in tag_names:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            keywords.append(name)
    return ', '.join(keywords)


def site_settings(request):
    if request.path.startswith('/panel/') or request.path.startswith('/admin/'):
        return {'site_settings': SiteSettings.get_solo()}

    settings = SiteSettings.get_solo()
    return {
        'site_settings': settings,
        'seo_keywords': build_seo_keywords(),
        'seo_description': (
            f'{settings.site_name} — кофе, десерты и уютная атмосфера. '
            f'{settings.address_street}. Тел. {settings.phone}.'
        ),
        'api_base_url': django_settings.API_BASE_URL,
    }
