# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_auto_20141222_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='results_html',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='last_run',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='project',
            field=models.ForeignKey(related_name='reports', to='reports.Project'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='results_json',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
