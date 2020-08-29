#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import Flask
from werkzeug.utils import import_string


extensions = [
    'zhihudaily.cache:cache',
    'zhihudaily.sentry:sentry_wrapper',
]

blueprints = [
    'zhihudaily.views.utils:utils',
    'zhihudaily.views.index:text_ui',
    'zhihudaily.views.with_image:image_ui',
    'zhihudaily.views.pages:pages_ui',
    'zhihudaily.views.three_columns:three_columns_ui',
]


def create_app(config):
    app = Flask('zhihudaily')
    app.config.from_object(config)

    for extention in extensions:
        extention = import_string(extention)
        extention.init_app(app)

    for blueprint in blueprints:
        blueprint = import_string(blueprint)
        app.register_blueprint(blueprint)

    @app.context_processor
    def inject_statics():
        return dict(debug=config.DEBUG)

    return app
