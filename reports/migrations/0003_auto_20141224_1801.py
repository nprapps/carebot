# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20141224_1754'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dimension',
            old_name='_percent_of_total',
            new_name='percent_of_total',
        ),
    ]
