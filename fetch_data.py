#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import sqlite3
import json
from os import path
import sys

import requests


session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                        x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})


def save(database, response):
    """Get someday's news info from the API and save to the database"""
    cursor = database.cursor()
    date = int(response.json()['date'])
    json_news = json.dumps(response.json()['news'])
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
    """Fetch news and init the database"""
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
    today = datetime.date.today().strftime("%Y%m%d")
    r = session.get(
        'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(today))
    save(database, r)
    check_integrity(database, date_range=10)
    database.close()


def check_integrity(database, date_range=10):
    """Check data integrity, make sure we won't miss a day"""
    cursor = database.cursor()
    date_in_db = []
    for date in cursor.execute('SELECT date FROM zhihudaily'):
        date_in_db.append(date[0])

    today = datetime.date.today()
    if date_range == 'all':
        birthday = datetime.date(2013, 5, 20)
        delta = (today - birthday).days
    else:
        delta = date_range
    date_in_real = []
    for i in range(1, delta+1):
        date = (today - datetime.timedelta(i)).strftime("%Y%m%d")
        date_in_real.insert(0, int(date))

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
    database = sqlite3.connect(database_path)
    if not path.exists(database_path):
        sys.argv.append(10)  # The default num of days is 10.
        num = sys.argv[1]
        print 'Start to init the database...'
        init_database(database, num)
    else:
        print "Add yestoday's news to database."
        daily_update(database)
