from django import template
register = template.Library()

@register.filter
def get_item(d, key):
    """
    Safe dict access in templates:
    {{ mydict|get_item:some_id }}
    Returns None if d isn't a dict or key doesn't exist.
    """
    try:
        return d.get(key)
    except Exception:
        return None
