# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reports',
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
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('start_date',)},
        ),
        migrations.AlterModelOptions(
            name='projectquery',
            options={'ordering': ('order',)},
        ),
        migrations.AlterField(
            model_name='projectquery',
            name='order',
            field=models.PositiveIntegerField(),
            preserve_default=True,
        ),
    ]
