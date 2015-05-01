#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from peewee import Model, IntegerField, CharField

from zhihudaily import database


class BaseModel(Model):
    class Meta:
        database = database


class Zhihudaily(BaseModel):
    date = IntegerField()
    json_news = CharField()
    display_date = CharField()


def create_tables():
    database.connect()
    database.create_tables([Zhihudaily])