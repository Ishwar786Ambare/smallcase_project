from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment

def count_queryset(value):
    if hasattr(value, 'count') and callable(value.count):
        return value.count()
    return len(value)

from datetime import datetime

# date filter
def date(value, format='%d %b %Y, %H:%M'):
    if value == 'now':
        value = datetime.now()
        
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    return ''

# round filter
def round_filter(value, precision=2):
    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return value

from django.contrib.messages import get_messages

def environment(**options):
    env = Environment(extensions=['jinja2.ext.i18n'], **options)
    
    # Install Django's translation functions
    from django.utils import translation
    from django.conf import settings
    env.install_gettext_translations(translation)
    
    env.globals.update({
        'static': static,   
        'url': reverse,
        'get_messages': get_messages,
        'get_language': translation.get_language,
        'LANGUAGES': settings.LANGUAGES,  # Available languages
    })
    env.filters['count'] = count_queryset
    env.filters['date'] = date
    env.filters['round'] = round_filter
    return env
