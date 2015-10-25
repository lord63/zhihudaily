#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime

from flask import render_template, Blueprint, request, redirect, url_for

from zhihudaily.utils import make_request, get_news_info, handle_image
from zhihudaily.cache import cache


text_ui = Blueprint('text_ui', __name__, template_folder='templates')


@text_ui.route('/')
@cache.cached(timeout=900)
def index():
    """The index page, for 文字 UI."""
    r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
    (display_date, date, news_list) = get_news_info(r)
    return render_template("index.html", lists=news_list,
                           display_date=display_date, date=date,
                           is_today=True)


# TODO: use our own database.
@text_ui.route('/before/<date>')
@cache.cached(timeout=900)
def before(date):
    """For 文字 UI and 图片 UI, before today."""
    r = make_request(
        'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date))
    (display_date, strdate, news_list) = get_news_info(r)
    today = datetime.date.today().strftime('%Y%m%d')
    day_after = (
        datetime.datetime.strptime(date, '%Y%m%d') + datetime.timedelta(1)
    ).strftime('%Y%m%d')
    if int(today) < int(date):
        if request.args['image'] == 'True':
            return redirect(url_for('image_ui.with_image'))
        else:
            return redirect(url_for('text_ui.index'))
    is_today = r.json().get('is_today', False)
    news_list = handle_image(news_list)
    if request.args['image'] == 'True':
        return render_template('with_image.html', lists=news_list,
                               display_date=display_date, date=strdate,
                               is_today=is_today, day_after=day_after)
    else:
        return render_template("index.html", lists=news_list,
                               display_date=display_date, date=strdate,
                               is_today=is_today, day_after=day_after)
