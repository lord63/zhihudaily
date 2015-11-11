#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime

from flask import render_template, Blueprint

from zhihudaily.utils import make_request
from zhihudaily.cache import cache


image_ui = Blueprint('image_ui', __name__, template_folder='templates')


@image_ui.route('/withimage')
@cache.cached(timeout=900)
def with_image():
    """The page for 图片 UI."""
    r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
    (display_date, date, news_list) = get_news_info(r)
    news_list = handle_image(news_list)
    day_before = (
        datetime.datetime.strptime(date, '%Y%m%d') - datetime.timedelta(1)
    ).strftime('%Y%m%d')
    return render_template('with_image.html', lists=news_list,
                           display_date=display_date,
                           day_before=day_before,
                           is_today=True)
