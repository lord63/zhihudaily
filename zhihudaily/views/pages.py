#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import render_template, Blueprint, json
from flask_paginate import Pagination

from zhihudaily.models import Zhihudaily
from zhihudaily.cache import cache


pages_ui = Blueprint('pages_ui', __name__, template_folder='templates')


@pages_ui.route('/pages', defaults={'page': 1})
@pages_ui.route('/pages/<int:page>')
@cache.cached(timeout=900)
def pages(page):
    """The page the 分页 UI."""
    db_news_list = (Zhihudaily.select()
                              .order_by(Zhihudaily.date.desc())
                              .paginate(page, 4))
    records = [
        {"news": json.loads(news.json_news), "display_date": news.display_date}
        for news in db_news_list
    ]
    pagination = Pagination(page=page, total=Zhihudaily.select().count(),
                            per_page=4, inner_window=7, outer_window=3,
                            css_framework='bootstrap3')

    return render_template('pages.html',
                           records=records,
                           pagination=pagination)
