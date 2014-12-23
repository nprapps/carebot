#!/usr/bin/env python

import codecs

from django.template import Context, loader

def render_to_file(template_name, data, filename):
    """
    Render a Django template directly to a file.
    """
    template = loader.get_template(template_name)
    ctx = Context(data)

    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(template.render(ctx))

def render_to_string(template_name, data, filename):
    """
    Render a Django template directly to a file.
    """
    template = loader.get_template(template_name)
    ctx = Context(data)

    return template.render(ctx)

