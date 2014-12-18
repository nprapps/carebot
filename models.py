#!/usr/bin/env python

from peewee import fn, Model, PostgresqlDatabase, BooleanField, CharField, DateTimeField, ForeignKeyField, IntegerField, TextField

import app_config

secrets = app_config.get_secrets()

db = PostgresqlDatabase(
    app_config.DATABASE['name'],
    user=app_config.DATABASE['user'],
    password=app_config.DATABASE['password'],
    host=app_config.DATABASE['host'],
    port=app_config.DATABASE['port']
)

class BaseModel(Model):
    """
    Base class for Peewee models. Ensures they all live in the same database.
    """
    class Meta:
        database = db

class Query(BaseModel):
    name = CharField()
    clan_yaml = TextField()

    def projects(self):
        return (Project
            .select()
            .join(ProjectQuery, on=ProjectQuery.project)
            .where(ProjectQuery.query == self)
        )

class Project(BaseModel):
    name = CharField()
    ga_property_id = CharField(default='53470309')
    domain = CharField(default='apps.npr.org')
    url_prefix = CharField()
    launch_date = CharField()

    def __unicode__(self):
        return u'%s Carebot Project' % self.name

    def queries(self):
        return (Query
            .select()
            .join(ProjectQuery, on=ProjectQuery.query)
            .where(ProjectQuery.project == self)
        )

    # TODO: automatically add asic queries on create

class ProjectQuery(BaseModel):
    query = ForeignKeyField(Query)
    project = ForeignKeyField(Project)

