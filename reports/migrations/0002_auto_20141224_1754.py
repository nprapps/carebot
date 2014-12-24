# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='query',
            options={'ordering': ('name',), 'verbose_name_plural': 'queries'},
        ),
        migrations.AlterModelOptions(
            name='social',
            options={'ordering': ('project__start_date',), 'verbose_name': 'social count', 'verbose_name_plural': 'social counts'},
        ),
        migrations.RenameField(
            model_name='dimension',
            old_name='percent_of_total',
            new_name='_percent_of_total',
        ),
    ]
