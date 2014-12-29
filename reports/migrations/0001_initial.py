# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DimensionResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=128)),
                ('_value', models.CharField(max_length=128)),
                ('percent_of_total', models.FloatField(null=True)),
                ('project_title', models.CharField(max_length=128)),
                ('report_ndays', models.PositiveIntegerField(null=True)),
                ('query_name', models.CharField(max_length=128)),
                ('metric_name', models.CharField(max_length=128)),
                ('metric_data_type', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ('metric', 'order'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MetricResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=128)),
                ('data_type', models.CharField(max_length=30)),
                ('project_title', models.CharField(max_length=128)),
                ('report_ndays', models.PositiveIntegerField(null=True)),
                ('query_name', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ('query_result', 'order'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('slug', models.SlugField(max_length=128, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('property_id', models.CharField(default=b'53470309', max_length=10)),
                ('domain', models.CharField(default=b'apps.npr.org', max_length=128)),
                ('prefix', models.CharField(max_length=128)),
                ('start_date', models.DateField()),
            ],
            options={
                'ordering': ('-start_date',),
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
                ('slug', models.SlugField(max_length=128, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(default=b'', max_length=256)),
                ('clan_yaml', models.TextField()),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'queries',
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
                ('project_title', models.CharField(max_length=128)),
                ('report_ndays', models.PositiveIntegerField(null=True)),
                ('query_name', models.CharField(max_length=128)),
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
                ('ndays', models.PositiveIntegerField(null=True)),
                ('results_json', models.TextField()),
                ('last_run', models.DateTimeField(null=True)),
                ('pageviews', models.PositiveIntegerField(null=True)),
                ('unique_pageviews', models.PositiveIntegerField(null=True)),
                ('users', models.PositiveIntegerField(null=True)),
                ('sessions', models.PositiveIntegerField(null=True)),
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
                'ordering': ('-project__start_date',),
                'verbose_name': 'social count',
                'verbose_name_plural': 'social counts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('slug', models.CharField(max_length=32, serialize=False, primary_key=True)),
            ],
            options={
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
            model_name='project',
            name='tags',
            field=models.ManyToManyField(to='reports.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='metricresult',
            name='query_result',
            field=models.ForeignKey(related_name='metrics', to='reports.QueryResult'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dimensionresult',
            name='metric',
            field=models.ForeignKey(related_name='dimensions', to='reports.MetricResult', null=True),
            preserve_default=True,
        ),
    ]
