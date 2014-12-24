# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_auto_20141224_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.CharField(default=b'App', max_length=32, choices=[(b'app', b'App'), (b'seamus-graphic', b'Seamus Graphic'), (b'lookatthis-post', b'Look At This Post')]),
            preserve_default=True,
        ),
    ]
