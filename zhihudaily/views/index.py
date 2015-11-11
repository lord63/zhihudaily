#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime

from flask import render_template, Blueprint, request, redirect, url_for, json

from zhihudaily.utils import make_request
from zhihudaily.cache import cache
from zhihudaily.models import Zhihudaily


text_ui = Blueprint('text_ui', __name__, template_folder='templates')


@text_ui.route('/')
@cache.cached(timeout=900)
def index():
    """The index page, for 文字 UI."""

    r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
    (display_date, date, news_list) = get_news_info(r)
    day_before = (
        datetime.datetime.strptime(date, '%Y%m%d') - datetime.timedelta(1)
    ).strftime('%Y%m%d')
    return render_template("index.html", lists=news_list,
                           display_date=display_date,
                           day_before=day_before,
                           is_today=True)


def full_request_path():
    """Make a key that includes GET parameters."""
    return request.full_path


@text_ui.route('/news/<date>')
@cache.cached(timeout=900, key_prefix=full_request_path)
def before(date):
    """For 文字 UI and 图片 UI, before today."""

    today = datetime.date.today().strftime('%Y%m%d')
    if int(today) <= int(date):
        if request.args.get('image', 'False') == 'True':
            return redirect(url_for('image_ui.with_image'))
        else:
            return redirect(url_for('text_ui.index'))

    news = Zhihudaily.select().where(Zhihudaily.date == int(date)).get()
    display_date, news_list = news.display_date, json.loads(news.json_news)

    day_before = (
        datetime.datetime.strptime(date, '%Y%m%d') - datetime.timedelta(1)
    ).strftime('%Y%m%d')
    day_after = (
        datetime.datetime.strptime(date, '%Y%m%d') + datetime.timedelta(1)
    ).strftime('%Y%m%d')

    template_name = {
        'False': 'index.html', 'True': 'with_image.html'
    }.get(request.args['image'], 'False')

    return render_template(template_name, lists=news_list,
                           display_date=display_date,
                           day_before=day_before,
                           day_after=day_after,
                           is_today=False)
