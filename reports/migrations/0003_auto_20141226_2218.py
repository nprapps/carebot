# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20141226_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dimensionresult',
            name='report_ndays',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='metricresult',
            name='report_ndays',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='queryresult',
            name='report_ndays',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
    ]
