#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    request = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
    date = request.json()['display_date']
    news_list = [
        [item['title'], item['share_url']] for item in request.json()['news']]
    story_list = [
        [item['title'], item['share_url']] for item in request.json()['top_stories']]
    lists = story_list + news_list
    return render_template("index.html", lists=lists, date=date)


if __name__ == '__main__':
    app.run(debug=True)
