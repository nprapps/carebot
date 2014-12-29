#!/usr/bin/env python

from django import template

register = template.Library()

@register.simple_tag
def social_per_session(project, metric):
    if metric == 'total':
        value = project.social.total()
    else:
        value = getattr(project.social, metric)

    sessions = project.all_time_report.sessions

    if not sessions:
        return 0

    return '%.2f' % (float(value) / sessions)


