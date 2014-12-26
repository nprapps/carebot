# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='ndays',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
    ]
