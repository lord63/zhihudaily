#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

import datetime
import json
from urlparse import urljoin

from werkzeug.contrib.atom import AtomFeed
from flask import request, Blueprint


from zhihudaily.utils import make_request
from zhihudaily.configs import Config
from zhihudaily.cache import cache


feeds = Blueprint('feeds', __name__, template_folder='templates')
redis_server = Config.redis_server


@feeds.route('/feeds')
@cache.cached(timeout=1200)
def generate_feed():
    feed = AtomFeed('Zhihudaily',
                    feed_url=request.url,
                    url=request.url_root)
    latest_url = 'http://news.at.zhihu.com/api/1.2/news/latest'
    if redis_server.get(latest_url):
        response_json = json.loads(redis_server.get(latest_url))
    else:
        response_json = make_request(latest_url).json()
        redis_server.setex(latest_url, (60*60), json.dumps(response_json))

    articles = response_json['news']
    for article in articles:
        if redis_server.get(article['url']):
            body = redis_server.get(article['url']).decode('utf-8')
        else:
            body = make_request(article['url']).json()['body']
            redis_server.setex(article['url'], (60*60*24), body)
        feed.add(article['title'], body,
                 content_type='html',
                 author='zhihudaily',
                 url=urljoin(request.url_root, article['url']),
                 updated=datetime.datetime.now())
    return feed.get_response()
