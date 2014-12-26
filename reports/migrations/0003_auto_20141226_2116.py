# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20141226_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='pageviews',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='sessions',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='unique_pageviews',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='users',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
    ]
