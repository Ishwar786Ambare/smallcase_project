from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment

def count_queryset(value):
    if hasattr(value, 'count') and callable(value.count):
        return value.count()
    return len(value)

# date filter
def date(value, format='%d %b %Y, %H:%M'):
    print('-'*50)
    print(value)
    print('-'*50)
    return value.strftime(format)

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,   
        'url': reverse,
    })
    env.filters['count'] = count_queryset
    env.filters['date'] = date
    return env