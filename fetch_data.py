#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import sqlite3
import json
from os import path
import re
import sys

import requests


session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                        x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})


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


def save(database, response):
    """Get someday's news info from the API and save to the database"""
    cursor = database.cursor()
    date = int(response.json()['date'])
    json_news = json.dumps(handle_image(response.json()['news']))
    display_date = response.json()['display_date']
    try:
        cursor.execute('INSERT INTO zhihudaily VALUES (?, ?, ?, ?)',
                       (1, date, json_news, display_date))
        database.commit()
    except sqlite3.IntegrityError:  # if the record has been stored before
        pass
    except Exception as error:
        print error


def init_database(database, num):
    """Fetch news and init the database

    :param num: int number or 'all'.
                the int number stands for the number of days to fetch;
                string 'all' means fetch all the news start from 20130519.
    """

    print 'Start to init the database...'
    cursor = database.cursor()
    cursor.execute('CREATE TABLE zhihudaily ('
                   'id integer ,'
                   'date integer primary key,'
                   'json_news varchar,'
                   'display_date varchar)')
    today = datetime.date.today()
    if num == 'all':
        # zhihudaily's birthday is 20130519
        birthday = datetime.date(2013, 5, 20)
        delta = (today - birthday).days
    else:
        delta = int(num)
    print 'There are {0} records to be fatched.'.format(delta)
    for i in range(delta):
        date = (today - datetime.timedelta(i)).strftime("%Y%m%d")
        r = session.get(
            'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date))
        save(database, r)
        print '\rcollect {0} records'.format(i+1),
        sys.stdout.flush()
    database.close()


def daily_update(database):
    """Fetch yestoday's news and save to database"""

    print "Adding yestoday's news to database..."
    today = datetime.date.today().strftime("%Y%m%d")
    r = session.get(
        'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(today))
    save(database, r)
    print "Checking date integrity..."
    check_integrity(database, date_range=10)
    database.close()


def check_integrity(database, date_range=10):
    """Check data integrity, make sure we won't miss a day

    :param date_range: int number or 'all'.
                       the int number stands for the range of days to check;
                       string 'all' means check data from start 20130519.
    """

    cursor = database.cursor()
    today = datetime.date.today()

    if type(date_range) == int:
        date_in_db = [
            date[0] for date in
            cursor.execute(
                ('SELECT date FROM zhihudaily ORDER BY date DESC '
                 'LIMIT {0}').format(date_range)
            )
        ]
        delta = date_range
    elif date_range == 'all':
        date_in_db = [
            date[0] for date in cursor.execute('SELECT date FROM zhihudaily')
        ]
        birthday = datetime.date(2013, 5, 20)
        delta = (today - birthday).days
    else:
        raise TypeError("Bad parameter date_range, "
                        "should be an integer or string value 'all'.")

    date_in_real = [
        int((today - datetime.timedelta(i)).strftime("%Y%m%d"))
        for i in range(1, delta+1)
    ]
    missed_date = set(date_in_real) - set(date_in_db)
    for date in missed_date:
        date_in_datetime = datetime.date(
            *[date / 10000, date % 10000 / 100, date % 100])
        date_ = (date_in_datetime + datetime.timedelta(1)).strftime("%Y%m%d")
        r = session.get(
            'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date_))
        print "fetching {0}...".format(date)
        save(database, r)
    database.close()


if __name__ == '__main__':
    database_path = path.join(path.dirname(path.abspath(__file__)),
                              'zhihudaily/zhihudaily.db')
    if not path.exists(database_path):
        database = sqlite3.connect(database_path)
        sys.argv.append(10)  # The default num of days is 10.
        num = sys.argv[1]
        init_database(database, num)
    else:
        database = sqlite3.connect(database_path)
        daily_update(database)
