from django import template
from django.template.loader import render_to_string
register = template.Library()

@register.simple_tag
def contribution_table(contributions):
    return render_to_string('dcdata/contribution/table.html', {'contributions': contributions})
