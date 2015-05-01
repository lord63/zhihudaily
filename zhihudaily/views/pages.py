#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import json

from flask import render_template
from flask.ext.paginate import Pagination

from zhihudaily import app
from zhihudaily.models import Zhihudaily
from zhihudaily.utils import make_request, get_news_info, handle_image


@app.route('/pages')
@app.route('/pages/<int:page>')
def pages(page=1):
    """The page the 分页 UI."""
    r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
    (display_date, date, news_list) = get_news_info(r)
    news_list = handle_image(news_list)
    news = Zhihudaily.select().order_by(
        Zhihudaily.date.desc()).paginate(page, 4)
    records = []
    for i in news:
        news = handle_image(json.loads(i.json_news))
        records.append({"date": i.date, "news": news,
                        "display_date": i.display_date})
    pagination = Pagination(page=page, total=Zhihudaily.select().count(),
                            per_page=4, inner_window=7, outer_window=3,
                            css_framework='bootstrap3')
    return render_template('pages.html', lists=news_list,
                           display_date=display_date, date=date,
                           page=page, records=records,
                           pagination=pagination)
