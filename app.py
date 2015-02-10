#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

import requests
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    date = request.args.get('date')
    if date:
        r = session.get(
            'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date))
        story_list = []
    else:
        r = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
        print 'yes'
        story_list = [
            [item['title'], item['share_url']] for item in r.json()['top_stories']]
    display_date = r.json()['display_date']
    date = r.json()["date"]
    news_list = [
        [item['title'], item['share_url']] for item in r.json()['news']]
    lists = story_list + news_list
    return render_template("index.html", lists=lists, display_date=display_date, date=date)


if __name__ == '__main__':
    app.run(debug=True)
