#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

import requests
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/before/<date>')
def before(date):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    r = session.get(
        'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date))
    display_date = r.json()['display_date']
    date = r.json()["date"]
    news_list = [
        [item['title'], item['share_url']] for item in r.json()['news']]
    return render_template("index.html", lists=news_list,
                           display_date=display_date, date=date)


@app.route('/')
def index():
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    date = request.args.get('date')
    r = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
    display_date = r.json()['display_date']
    date = r.json()["date"]
    news_list = [
        [item['title'], item['share_url']] for item in r.json()['news']]
    return render_template("index.html", lists=news_list,
                           display_date=display_date, date=date)


if __name__ == '__main__':
    app.run(debug=True)
