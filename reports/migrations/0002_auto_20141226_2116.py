# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='pageviews',
            field=models.PositiveIntegerField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='report',
            name='sessions',
            field=models.PositiveIntegerField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='report',
            name='unique_pageviews',
            field=models.PositiveIntegerField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='report',
            name='users',
            field=models.PositiveIntegerField(default=None),
            preserve_default=False,
        ),
    ]
