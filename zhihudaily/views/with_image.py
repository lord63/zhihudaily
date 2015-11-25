#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals


from flask import render_template, Blueprint, json

from zhihudaily.cache import cache
from zhihudaily.models import Zhihudaily
from zhihudaily.utils import Date


image_ui = Blueprint('image_ui', __name__, template_folder='templates')


@image_ui.route('/withimage')
@cache.cached(timeout=900)
def with_image():
    """The page for 图片 UI."""
    day = Date()
    news = Zhihudaily.get(Zhihudaily.date == int(day.today))

    return render_template('with_image.html',
                           lists=json.loads(news.json_news),
                           display_date=news.display_date,
                           day_before=day.day_before)
