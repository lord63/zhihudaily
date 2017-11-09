#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from flask import render_template, jsonify, Blueprint, json

from zhihudaily.models import Zhihudaily
from zhihudaily.utils import Date
from zhihudaily.cache import cache
from zhihudaily.crawler import Crawler


three_columns_ui = Blueprint('three_columns_ui', __name__,
                             template_folder='templates')


@three_columns_ui.route('/three-columns')
@cache.cached(timeout=3600)
def three_columns():
    """The page for 三栏 UI"""
    day = Date()
    days = day.date_range(20)
    return render_template('three_columns.html', days=days)


@three_columns_ui.route('/three-columns/<date>')
@cache.cached(timeout=900)
def show_titles(date):
    """Get titles via AJAX."""
    news = Zhihudaily.get(Zhihudaily.date == date)
    json_news = json.loads(news.json_news)
    return jsonify(news=json_news)


@three_columns_ui.route('/three-columns/append-date/<date>')
@cache.cached(timeout=10800)
def append_date(date):
    """Append dates when scroll to bottom via AJAX"""
    day = Date(date)
    append_list = day.date_range(16)[1:]
    return jsonify(append_list=append_list)


@three_columns_ui.route('/three-columns/contents/<id>')
@cache.cached(timeout=10800)
def get_content(id):
    r = Crawler().send_request('https://news-at.zhihu.com/api/4/news/' + id)
    return jsonify(body=r.json()['body'])
