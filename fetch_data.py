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


def init_database(database):
    """Get all the news from 2013.05.19 to yestoday and save to database"""
    cursor = database.cursor()
    cursor.execute('CREATE TABLE zhihudaily (id integer ,'
                                            'date integer primary key,'
                                            'json_news varchar,'
                                            'display_date varchar)'
    )
    today = datetime.date.today()
    birthday = datetime.date(2013, 5, 20)  # zhihudaily's birthday is 20130519
    delta = (today - birthday).days
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
    database.close()


if __name__ == '__main__':
    database_path = path.dirname(path.abspath(__file__)) + '/zhihudaily.db'
    if not path.exists(database_path):
        print 'Start to init the database...'
        database = sqlite3.connect(database_path)
        init_database(database)
    else:
        print "Add yestoday's news to database."
        database = sqlite3.connect(database_path)
        daily_update(database)