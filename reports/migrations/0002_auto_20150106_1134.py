# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('slug',)},
        ),
        migrations.AddField(
            model_name='query',
            name='is_comparable',
            field=models.BooleanField(default=True, help_text=b'Should this query be available for cross-project comparison.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='query',
            name='description',
            field=models.CharField(default=b'', max_length=256, blank=True),
            preserve_default=True,
        ),
    ]
