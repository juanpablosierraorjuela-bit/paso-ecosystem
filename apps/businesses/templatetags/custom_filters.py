from django import template
register = template.Library()

@register.filter
def split_day(value):
    try:
        if ':' in value:
            parts = value.split(':')
            return {'index': parts[0], 'number': parts[1]}
    except:
        pass
    return {'index': 0, 'number': ''}
