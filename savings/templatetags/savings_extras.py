from django import template

register = template.Library()

@register.filter
def filter_completed(goals):
    return [goal for goal in goals if goal.completed] 