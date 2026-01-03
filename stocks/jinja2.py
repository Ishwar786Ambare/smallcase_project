from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment

def count_queryset(value):
    if hasattr(value, 'count') and callable(value.count):
        return value.count()
    return len(value)

# date filter
def date(value, format='%d %b %Y, %H:%M'):
    if value:
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
    env = Environment(**options)
    env.globals.update({
        'static': static,   
        'url': reverse,
        'get_messages': get_messages,
    })
    env.filters['count'] = count_queryset
    env.filters['date'] = date
    env.filters['round'] = round_filter
    return env
