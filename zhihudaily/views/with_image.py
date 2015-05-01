#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals


from flask import render_template

from zhihudaily import app
from zhihudaily.utils import make_request, get_news_info, handle_image


@app.route('/withimage')
def with_image():
    """The page for 图片 UI."""
    r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
    (display_date, date, news_list) = get_news_info(r)
    news_list = handle_image(news_list)
    return render_template('with_image.html', lists=news_list,
                           display_date=display_date, date=date,
                           is_today=True)


