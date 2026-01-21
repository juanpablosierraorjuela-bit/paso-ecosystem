from django import template
register = template.Library()

@register.filter(name='split_day')
def split_day(value):
    if not value: return ["", ""]
    if ":" in str(value): return value.split(":")
    return [value, value]
