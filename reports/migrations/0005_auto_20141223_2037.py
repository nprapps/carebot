# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_auto_20141223_1846'),
    ]

    operations = [
        migrations.CreateModel(
            name='Social',
            fields=[
                ('project', models.OneToOneField(primary_key=True, serialize=False, to='reports.Project')),
                ('facebook_likes', models.PositiveIntegerField(default=0)),
                ('facebook_shares', models.PositiveIntegerField(default=0)),
                ('facebook_comments', models.PositiveIntegerField(default=0)),
                ('twitter', models.PositiveIntegerField(default=0)),
                ('google', models.PositiveIntegerField(default=0)),
                ('pinterest', models.PositiveIntegerField(default=0)),
                ('linkedin', models.PositiveIntegerField(default=0)),
                ('stumbleupon', models.PositiveIntegerField(default=0)),
                ('last_update', models.DateTimeField(null=True)),
            ],
            options={
                'ordering': ('project__start_date',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ('project__start_date', 'ndays')},
        ),
    ]
