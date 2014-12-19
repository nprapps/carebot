# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=128)),
                ('title', models.CharField(max_length=128)),
                ('property_id', models.CharField(default=b'53470309', max_length=10)),
                ('domain', models.CharField(default=b'apps.npr.org', max_length=128)),
                ('prefix', models.CharField(max_length=128)),
                ('start_date', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField()),
                ('project', models.ForeignKey(to='reports.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('clan_yaml', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='projectquery',
            name='query',
            field=models.ForeignKey(to='reports.Query'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='queries',
            field=models.ManyToManyField(to='reports.Query', through='reports.ProjectQuery'),
            preserve_default=True,
        ),
    ]
