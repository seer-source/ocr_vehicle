from django import template

register = template.Library()

@register.filter
def get_item(value, index):
    try:
        return value[index]
    except (IndexError, TypeError):
        return None
@register.filter
def get_formatted_duration(duration):
    if duration:
        duration_seconds = duration.total_seconds()
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}"
    else:
        return ""