#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from flask import render_template, Blueprint, request, redirect, url_for, json

from zhihudaily.utils import Date
from zhihudaily.cache import cache
from zhihudaily.models import Zhihudaily


text_ui = Blueprint('text_ui', __name__, template_folder='templates')


@text_ui.route('/')
@cache.cached(timeout=900)
def index():
    """The index page, for 文字 UI."""
    news = Zhihudaily.select().order_by(Zhihudaily.date.desc()).first()
    day = Date(news.date)

    return render_template("index.html",
                           lists=json.loads(news.json_news),
                           display_date=news.display_date,
                           day_before=day.day_before)


def full_request_path():
    """Make a key that includes GET parameters."""
    return request.full_path


@text_ui.route('/news/<date>')
@cache.cached(timeout=900, key_prefix=full_request_path)
def before(date):
    """For 文字 UI and 图片 UI, before today."""

    day = Date(date)
    if day.today <= date:
        if request.args.get('image', 'False') == 'True':
            return redirect(url_for('image_ui.with_image'))
        else:
            return redirect(url_for('text_ui.index'))

    news = Zhihudaily.get(Zhihudaily.date == date)

    template_name = {
        'False': 'index.html', 'True': 'with_image.html'
    }[request.args.get('image', 'False')]

    return render_template(template_name,
                           lists=json.loads(news.json_news),
                           display_date=news.display_date,
                           day_before=day.day_before,
                           day_after=day.day_after)