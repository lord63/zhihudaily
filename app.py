#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import ceil
import json
import datetime

import requests
from flask import Flask, render_template, request, g, redirect, url_for
from peewee import *


app = Flask(__name__)
app.config.from_object(__name__)
SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'

database = SqliteDatabase('zhihudaily.db')


class BaseModel(Model):
    class Meta:
        database = database


class Zhihudaily(BaseModel):
    date = IntegerField()
    json_news = CharField()


def create_tables():
    database.connect()
    database.create_tables([Zhihudaily])


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/before/<date>')
@app.route('/withimage/before/<date>')
def before(date):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    r = session.get(
        'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date))
    display_date = r.json()['display_date']
    today = datetime.date.today().strftime('%Y%m%d')
    strdate = r.json()["date"]
    day_after = (datetime.datetime.strptime(date, '%Y%m%d') + datetime.timedelta(1)).strftime('%Y%m%d')
    if int(today) < int(date):
        return redirect(url_for('index'))
    is_today = r.json().get('is_today', False)
    news_list = [item for item in r.json()['news']]
    if 'withimage' in request.url:
        return render_template('with_image.html', lists=news_list,
                               display_date=display_date, date=strdate,
                               is_today=is_today, day_after=day_after)
    else:
        return render_template("index.html", lists=news_list,
                               display_date=display_date, date=strdate,
                               is_today=is_today, day_after=day_after)


@app.route('/')
def index():
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    r = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
    display_date = r.json()['display_date']
    date = r.json()['date']
    news_list = [item for item in r.json()['news']]
    return render_template("index.html", lists=news_list,
                           display_date=display_date, date=date,
                           is_today=True)


@app.route('/withimage')
def with_image():
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    r = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
    display_date = r.json()['display_date']
    date = r.json()["date"]
    news_list = [item for item in r.json()['news']]
    request.environ['Referer'] = 'http://daily.zhihu.com/'
    return render_template('with_image.html', lists=news_list,
                           display_date=display_date, date=date)


@app.route('/pages')
@app.route('/pages/<int:page>')
def pages(page=1):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    r = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
    display_date = r.json()['display_date']
    date = r.json()["date"]
    news_list = [item for item in r.json()['news']]
    request.environ['Referer'] = 'http://daily.zhihu.com/'
    news = Zhihudaily.select().paginate(page, 7)
    records = []
    for i in news:
        temp = json.loads(i.json_news)
        records.append({"date": i.date, "news": temp})
    pages = int(ceil(Zhihudaily.select().count() / 7))
    return render_template('pages.html', lists=news_list,
                           display_date=display_date, date=date,
                           page=page, records=records, pages=pages)


@app.route('/pagination')
def pagination():
    pages = int(ceil(Zhihudaily.select().count() / 7))
    return render_template('pagination.html', pages=pages)


if __name__ == '__main__':
    app.run(debug=True)
