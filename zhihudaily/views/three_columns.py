#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime
import json

from flask import render_template, jsonify, Blueprint

from zhihudaily.models import Zhihudaily
from zhihudaily.utils import make_request


three_columns_ui = Blueprint('three_columns_ui', __name__,
                             template_folder='templates')


@three_columns_ui.route('/three-columns')
def three_columns():
    """The page for 三栏 UI"""
    today = datetime.date.today()
    days = []
    for i in range(20):
        days.append((today - datetime.timedelta(i)).strftime('%Y%m%d'))
    return render_template('three_columns.html', days=days)


@three_columns_ui.route('/three-columns/<date>')
def show_titles(date):
    """Get titles via AJAX."""
    today = datetime.date.today().strftime('%Y%m%d')
    if today == date:
        r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
        news = [{'title': item['title'],
                 'url': item['share_url'],
                 'id': item['id']} for item in r.json()['news']]
    else:
        the_day = Zhihudaily.get(Zhihudaily.date == int(date))
        json_news = json.loads(the_day.json_news)
        news = [{'title': item['title'],
                 'url': item['share_url'],
                 'id': item['id']} for item in json_news]
    return jsonify(news=news)


@three_columns_ui.route('/three-columns/append-date/<date>')
def append_date(date):
    """Append dates when scroll to bottom via AJAX"""
    date_obj = datetime.datetime.strptime(date, '%Y%m%d').date()
    append_list = []
    for i in range(1, 16):
        to_be_appended = (date_obj - datetime.timedelta(i)).strftime('%Y%m%d')
        append_list.append(to_be_appended)
    return jsonify(append_list=append_list)


@three_columns_ui.route('/three-columns/contents/<id>')
def get_content(id):
    r = make_request('http://news-at.zhihu.com/api/4/news/' + id)
    return jsonify(body=r.json()['body'])
