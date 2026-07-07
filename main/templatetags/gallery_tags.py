from django import template

register = template.Library()


@register.filter
def aspect_class(ratio):
    if not ratio or ratio == 'auto':
        return ''
    return f'gallery-item--{ratio.replace(":", "-")}'
