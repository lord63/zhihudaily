#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import os
import re
from StringIO import StringIO

import requests
from flask import Flask, render_template, request, g, redirect, url_for, send_file
from flask.ext.paginate import Pagination
from peewee import *
import redis


SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'

app = Flask(__name__)
app.config.from_object(__name__)


db = os.path.dirname(os.path.abspath(__file__)) + '/zhihudaily.db'
database = SqliteDatabase(db)
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                        x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})


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
    r = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
    display_date = r.json()['display_date']
    date = r.json()['date']
    news_list = [item for item in r.json()['news']]
    return render_template("index.html", lists=news_list,
                           display_date=display_date, date=date,
                           is_today=True)


@app.route('/withimage')
def with_image():
    r = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
    display_date = r.json()['display_date']
    date = r.json()["date"]
    news_list = [item for item in r.json()['news']]
    for news in news_list:
        items = re.search(r'(?<=http://)(.*?)\.zhimg.com/(.*)$', news['image']).groups()
        news['image'] = 'http://zhihudaily.lord63.com/img/{0}/{1}'.format(items[0], items[1])
    return render_template('with_image.html', lists=news_list,
                           display_date=display_date, date=date,
                           is_today=True)


@app.route('/pages')
@app.route('/pages/<int:page>')
def pages(page=1):
    r = session.get('http://news.at.zhihu.com/api/1.2/news/latest')
    display_date = r.json()['display_date']
    date = r.json()["date"]
    news_list = [item for item in r.json()['news']]
    request.environ['Referer'] = 'http://daily.zhihu.com/'
    news = Zhihudaily.select().order_by(
        Zhihudaily.date.desc()).paginate(page, 4)
    records = []
    for i in news:
        temp = json.loads(i.json_news)
        records.append({"date": i.date, "news": temp,
                        "display_date": i.display_date})
    pagination = Pagination(page=page, total=Zhihudaily.select().count(),
                            per_page=4, inner_window=7, outer_window=3,
                            css_framework='bootstrap3')
    return render_template('pages.html', lists=news_list,
                           display_date=display_date, date=date,
                           page=page, records=records,
                           pagination=pagination)


@app.route('/img/<server>/<hash>')
def image(server, hash):
    image_url = 'http://{0}.zhimg.com/{1}'.format(server, hash)
    r = redis.StrictRedis(host='localhost', port=6379)
    cached = r.get(image_url)
    if cached:
        buffer_image = StringIO(cached)
        buffer_image.seek(0)
    else:
        response = session.get(image_url)
        buffer_image = StringIO(response.content)
        buffer_image.seek(0)
        r.setex(image_url, (60*60*24*7), buffer_image.getvalue())
    return send_file(buffer_image, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(debug=True)
