#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from StringIO import StringIO
import re

from flask import send_file, g
import requests

from zhihudaily import app
from zhihudaily import redis_server, database


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


def make_request(url):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    r = session.get(url)
    return r


def get_news_info(response):
    display_date = response.json()['display_date']
    date = response.json()['date']
    news_list = [item for item in response.json()['news']]
    return display_date, date, news_list


def handle_image(news_list):
    """Point all the images to my server, because use zhihudaily's
    images directly may get 403 error.
    """
    for news in news_list:
        items = re.search(r'(?<=http://)(.*?)\.zhimg.com/(.*)$',
                          news['image']).groups()
        news['image'] = (
            'http://zhihudaily.lord63.com/img/{0}/{1}'.format(
                items[0], items[1]))
    return news_list


@app.route('/img/<server>/<hash_string>')
def image(server, hash_string):
    """Handle image, use redis to cache image."""
    image_url = 'http://{0}.zhimg.com/{1}'.format(server, hash_string)
    cached = redis_server.get(image_url)
    if cached:
        buffer_image = StringIO(cached)
        buffer_image.seek(0)
    else:
        r = make_request(image_url)
        buffer_image = StringIO(r.content)
        buffer_image.seek(0)
        redis_server.setex(image_url, (60*60*24*7), buffer_image.getvalue())
    return send_file(buffer_image, mimetype='image/jpeg')