#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from peewee import Model, CharField

from zhihudaily.configs import Config


class BaseModel(Model):
    class Meta:
        database = Config.database


class Zhihudaily(BaseModel):
    date = CharField()
    json_news = CharField()
    display_date = CharField()


def create_tables():
    Config.database.connect()
    Config.database.create_table(Zhihudaily)
