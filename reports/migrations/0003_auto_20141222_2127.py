# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20141222_2120'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ndays', models.PositiveIntegerField()),
                ('results_json', models.TextField(editable=False)),
                ('last_run', models.DateTimeField(null=True, editable=False)),
                ('project', models.ForeignKey(to='reports.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='reports',
            name='project',
        ),
        migrations.DeleteModel(
            name='Reports',
        ),
    ]
