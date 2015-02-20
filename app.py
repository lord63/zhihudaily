#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import ceil
import json
import datetime
import os

import requests
from flask import Flask, render_template, request, g, redirect, url_for
from flask.ext.paginate import Pagination
from peewee import *


SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'

app = Flask(__name__)
app.config.from_object(__name__)

db = os.path.dirname(os.path.abspath(__file__)) + '/zhihudaily.db'
database = SqliteDatabase(db)


class BaseModel(Model):
    class Meta:
        database = database


class Zhihudaily(BaseModel):
    date = IntegerField()
    json_news = CharField()
    display_date = CharField()


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
def before(date):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    r = session.get(
        'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date))
    display_date = r.json()['display_date']
    today = datetime.date.today().strftime('%Y%m%d')
    strdate = r.json()["date"]
    day_after = (
        datetime.datetime.strptime(date, '%Y%m%d') + datetime.timedelta(1)
    ).strftime('%Y%m%d')
    if int(today) < int(date):
        if request.args['image'] == 'True':
            return redirect(url_for('with_image'))
        else:
            return redirect(url_for('index'))
    is_today = r.json().get('is_today', False)
    news_list = [item for item in r.json()['news']]
    if request.args['image'] == 'True':
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
                           display_date=display_date, date=date,
                           is_today=True)


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
    news = Zhihudaily.select().order_by(Zhihudaily.date.desc()).paginate(page, 7)
    records = []
    for i in news:
        temp = json.loads(i.json_news)
        records.append({"date": i.date, "news": temp,
                        "display_date": i.display_date})
    pagination = Pagination(page=page, total=Zhihudaily.select().count(), per_page=7,
                            inner_window=7, outer_window=3, css_framework='bootstrap3')
    return render_template('pages.html', lists=news_list,
                           display_date=display_date, date=date,
                           page=page, records=records,
                           pagination=pagination)


if __name__ == '__main__':
    app.run(debug=True)
