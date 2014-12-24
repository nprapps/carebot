# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dimension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=128)),
                ('_value', models.CharField(max_length=128)),
                ('percent_of_total', models.FloatField(null=True)),
            ],
            options={
                'ordering': ('metric', 'order'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=128)),
                ('data_type', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ('query_result', 'order'),
            },
            bases=(models.Model,),
        ),
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
                'ordering': ('start_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(default=b'', max_length=256)),
                ('clan_yaml', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QueryResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('sampled', models.BooleanField(default=False)),
                ('sample_size', models.PositiveIntegerField(default=0)),
                ('sample_space', models.PositiveIntegerField(default=0)),
                ('sample_percent', models.FloatField(default=100)),
                ('query', models.ForeignKey(related_name='query_results', to='reports.Query')),
            ],
            options={
                'ordering': ('report', 'order'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ndays', models.PositiveIntegerField()),
                ('results_json', models.TextField()),
                ('last_run', models.DateTimeField(null=True)),
            ],
            options={
                'ordering': ('project__start_date', 'ndays'),
            },
            bases=(models.Model,),
        ),
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
        migrations.AddField(
            model_name='report',
            name='project',
            field=models.ForeignKey(related_name='reports', to='reports.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='queryresult',
            name='report',
            field=models.ForeignKey(related_name='query_results', to='reports.Report'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectquery',
            name='project',
            field=models.ForeignKey(related_name='project_queries', to='reports.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectquery',
            name='query',
            field=models.ForeignKey(related_name='project_queries', to='reports.Query'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='queries',
            field=models.ManyToManyField(to='reports.Query', through='reports.ProjectQuery'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='metric',
            name='query_result',
            field=models.ForeignKey(related_name='metrics', to='reports.QueryResult'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dimension',
            name='metric',
            field=models.ForeignKey(related_name='dimensions', to='reports.Metric'),
            preserve_default=True,
        ),
    ]
