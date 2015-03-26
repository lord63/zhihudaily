#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import os
import re
from StringIO import StringIO

from flask import (Flask, render_template, request, g, redirect,
                   url_for, send_file, jsonify)
from flask.ext.paginate import Pagination
import requests
from peewee import *
import redis


app = Flask(__name__)
app.config.from_object(__name__)
db = os.path.dirname(os.path.abspath(__file__)) + '/zhihudaily.db'
database = SqliteDatabase(db)
SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'


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


def make_request(url):
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    r = session.get(url)
    return r


def get_news_info(response):
    display_date = response.json()['display_date']
    date = response.json()['date']
    news_list = [item for item in response.json()['news']]
    return display_date, date, news_list


def handle_image(news_list):
    """Point all the images to my server, because use zhihudaily's
    images directly may get 403 error.
    """
    for news in news_list:
        items = re.search(r'(?<=http://)(.*?)\.zhimg.com/(.*)$',
                          news['image']).groups()
        news['image'] = (
            'http://zhihudaily.lord63.com/img/{0}/{1}'.format(
                items[0], items[1]))
    return news_list


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
    """For 文字 UI and 图片 UI, before today."""
    r = make_request(
        'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date))
    (display_date, strdate, news_list) = get_news_info(r)
    today = datetime.date.today().strftime('%Y%m%d')
    day_after = (
        datetime.datetime.strptime(date, '%Y%m%d') + datetime.timedelta(1)
    ).strftime('%Y%m%d')
    if int(today) < int(date):
        if request.args['image'] == 'True':
            return redirect(url_for('with_image'))
        else:
            return redirect(url_for('index'))
    is_today = r.json().get('is_today', False)
    news_list = handle_image(news_list)
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
    """The index page, for 文字 UI."""
    r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
    (display_date, date, news_list) = get_news_info(r)
    return render_template("index.html", lists=news_list,
                           display_date=display_date, date=date,
                           is_today=True)


@app.route('/withimage')
def with_image():
    """The page for 图片 UI."""
    r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
    (display_date, date, news_list) = get_news_info(r)
    news_list = handle_image(news_list)
    return render_template('with_image.html', lists=news_list,
                           display_date=display_date, date=date,
                           is_today=True)


@app.route('/pages')
@app.route('/pages/<int:page>')
def pages(page=1):
    """The page the 分页 UI."""
    r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
    (display_date, date, news_list) = get_news_info(r)
    news_list = handle_image(news_list)
    news = Zhihudaily.select().order_by(
        Zhihudaily.date.desc()).paginate(page, 4)
    records = []
    for i in news:
        news = handle_image(json.loads(i.json_news))
        records.append({"date": i.date, "news": news,
                        "display_date": i.display_date})
    pagination = Pagination(page=page, total=Zhihudaily.select().count(),
                            per_page=4, inner_window=7, outer_window=3,
                            css_framework='bootstrap3')
    return render_template('pages.html', lists=news_list,
                           display_date=display_date, date=date,
                           page=page, records=records,
                           pagination=pagination)


@app.route('/three-columns')
def three_columns():
    today = int(datetime.date.today().strftime('%Y%m%d'))
    return render_template('three_columns.html', today=today)


@app.route('/three-columns/<date>')
def show_titles(date):
    today = datetime.date.today().strftime('%Y%m%d')
    if today == date:
        r = make_request('http://news.at.zhihu.com/api/1.2/news/latest')
        news = [{'title':item['title'], 'url': item['share_url']} for item in r.json()['news']]
    else:
        the_day = Zhihudaily.get(Zhihudaily.date == int(date))
        json_news = json.loads(the_day.json_news)
        news = [{'title':item['title'], 'url': item['share_url']} for item in json_news]
    return jsonify(news=news)


@app.route('/three-columns/append-date/<date>')
def append_date(date):
    date_obj = datetime.datetime.strptime(date, '%Y%m%d').date()
    append_list = []
    for i in range(1, 16):
        to_be_appended = (date_obj - datetime.timedelta(i)).strftime('%Y%m%d')
        append_list.append(to_be_appended)
    return jsonify(append_list=append_list)


@app.route('/img/<server>/<hash_string>')
def image(server, hash_string):
    """Handle image, use redis to cache image."""
    image_url = 'http://{0}.zhimg.com/{1}'.format(server, hash_string)
    redis_server = redis.StrictRedis(host='localhost', port=6379)
    cached = redis_server.get(image_url)
    if cached:
        buffer_image = StringIO(cached)
        buffer_image.seek(0)
    else:
        r = make_request(image_url)
        buffer_image = StringIO(r.content)
        buffer_image.seek(0)
        redis_server.setex(image_url, (60*60*24*7), buffer_image.getvalue())
    return send_file(buffer_image, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(debug=True)
