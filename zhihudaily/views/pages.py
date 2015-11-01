#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from flask import render_template, Blueprint, json
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
    if page == 1:
        r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
        (display_date, _, news_list) = get_news_info(r)
        today_news_list = handle_image(news_list)
    else:
        today_news_list = display_date = ''

    db_news_list = Zhihudaily.select().order_by(
        Zhihudaily.date.desc()).paginate(page, 4)
    records = [
        {"news": json.loads(news.json_news), "display_date": news.display_date}
        for news in db_news_list
    ]
    pagination = Pagination(page=page, total=Zhihudaily.select().count(),
                            per_page=4, inner_window=7, outer_window=3,
                            css_framework='bootstrap3')

    return render_template('pages.html', today_news_list=today_news_list,
                           display_date=display_date,
                           page=page, records=records,
                           pagination=pagination)
