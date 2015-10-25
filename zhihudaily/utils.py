#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import re

import requests

from zhihudaily.cache import cache


@cache.memoize(timeout=1200)
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
