# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20150106_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dimensionresult',
            name='name',
            field=models.CharField(max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='domain',
            field=models.CharField(default=b'apps.npr.org', max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='prefix',
            field=models.CharField(max_length=128, blank=True),
            preserve_default=True,
        ),
    ]
