from django import template

register = template.Library()

@register.simple_tag(name='fs_value')
def fs_value(flags, key, default_value):
    if key in flags:
        return flags[key]
    return default_value