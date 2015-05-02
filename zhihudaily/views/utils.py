#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from StringIO import StringIO

from flask import send_file, g, Blueprint

from zhihudaily.configs import Config
from zhihudaily.utils import make_request


utils = Blueprint('utils', __name__)


@utils.before_app_request
def before_request():
    g.db = Config.database
    g.db.connect()


@utils.after_app_request
def after_request(response):
    g.db.close()
    return response


@utils.route('/img/<server>/<hash_string>')
def image(server, hash_string):
    """Handle image, use redis to cache image."""
    image_url = 'http://{0}.zhimg.com/{1}'.format(server, hash_string)
    cached = Config.redis_server.get(image_url)
    if cached:
        buffer_image = StringIO(cached)
        buffer_image.seek(0)
    else:
        r = make_request(image_url)
        buffer_image = StringIO(r.content)
        buffer_image.seek(0)
        Config.redis_server.setex(image_url, (60*60*24*7),
                                  buffer_image.getvalue())
    return send_file(buffer_image, mimetype='image/jpeg')
