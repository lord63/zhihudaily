#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from werkzeug.contrib.atom import AtomFeed
from flask import request, Blueprint, json

from zhihudaily.cache import cache
from zhihudaily.configs import Config
from zhihudaily.models import Zhihudaily
from zhihudaily.utils import Date
from zhihudaily.crawler import Crawler
from zhihudaily._compat import urljoin


feeds = Blueprint('feeds', __name__, template_folder='templates')
redis_server = Config.redis_server


@feeds.route('/feeds')
@cache.cached(timeout=1200)
def generate_feed():
    """Code snippet from https://flask.pocoo.org/snippets/10/"""
    day = Date()
    feed = AtomFeed('Zhihudaily', feed_url=request.url, url=request.url_root)
    news = Zhihudaily.get(Zhihudaily.date == int(day.today))

    articles = json.loads(news.json_news)
    for article in articles:
        if redis_server.get(article['url']):
            body = redis_server.get(article['url']).decode('utf-8')
        else:
            body = Crawler().send_request(article['url']).json()['body']
            redis_server.setex(article['url'], (60*60*24), body)
        feed.add(article['title'], body,
                 content_type='html',
                 author='zhihudaily',
                 url=urljoin(request.url_root, article['url']),
                 updated=day.now)
    return feed.get_response()
