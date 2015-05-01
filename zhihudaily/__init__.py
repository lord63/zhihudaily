#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from flask import Flask
import os
from peewee import SqliteDatabase
import redis


app = Flask(__name__)
db = os.path.dirname(os.path.abspath(__file__)) + '/zhihudaily.db'
database = SqliteDatabase(db)
redis_server = redis.StrictRedis(host='localhost', port=6379)

from .views.index import text_ui
from .views.with_image import image_ui
from .views.pages import pages_ui
from .views.three_columns import three_columns_ui

app.register_blueprint(text_ui)
app.register_blueprint(image_ui)
app.register_blueprint(pages_ui)
app.register_blueprint(three_columns_ui)