#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import json

from flask import render_template, Blueprint
from flask.ext.paginate import Pagination

from zhihudaily.models import Zhihudaily
from zhihudaily.utils import make_request, get_news_info, handle_image
from zhihudaily.cache import cache


pages_ui = Blueprint('pages_ui', __name__, template_folder='templates')


@pages_ui.route('/pages')
@pages_ui.route('/pages/<int:page>')
@cache.cached(timeout=900)
def pages(page=1):
    """The page the 分页 UI."""
    # TODO: don't send useless requests.
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
