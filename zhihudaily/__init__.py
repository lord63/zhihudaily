#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from flask import Flask
from zhihudaily.cache import cache


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    cache.init_app(app)

    from .views.utils import utils
    from .views.index import text_ui
    from .views.with_image import image_ui
    from .views.pages import pages_ui
    from .views.three_columns import three_columns_ui
    from .views.feeds import feeds

    app.register_blueprint(utils)
    app.register_blueprint(text_ui)
    app.register_blueprint(image_ui)
    app.register_blueprint(pages_ui)
    app.register_blueprint(three_columns_ui)
    app.register_blueprint(feeds)

    return app
