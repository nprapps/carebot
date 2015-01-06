#!/usr/bin/env python

from django import template

register = template.Library()

@register.simple_tag
def social_per_1000_sessions(project, metric):
    if metric == 'total':
        value = project.social.total()
    else:
        value = getattr(project.social, metric)

    sessions = project.all_time_report.sessions
    fb_shares = project.social.facebook_shares

    if not sessions:
        return 0

    if metric == 'facebook_likes' or metric == 'facebook_comments':
        return '%.2f' % (float(value) / fb_shares)
    else:
        return '%.2f' % (float(value) / (sessions / 1000))


