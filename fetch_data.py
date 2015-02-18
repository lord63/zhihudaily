#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import sqlite3
import json
import os
import sys

import requests


def init_database():
    db = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) +
                         '/zhihudaily.db')
    cursor = db.cursor()
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux \
                            x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'})
    today = datetime.date.today()
    birthday = datetime.date(2013, 5, 20)  # zhihudaily's birthday is 20130519
    delta = (today - birthday).days
    print 'There are {0} records to be fatched.'.format(delta)
    for i in range(-1, delta):  # the first time I need to create the table
        if i % 10 == 0:
            print '\rcollect {0} records'.format(i),
            sys.stdout.flush()
        date = (today - datetime.timedelta(i)).strftime("%Y%m%d")
        r = session.get(
            'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(date))
        date = int(r.json()['date'])
        json_news = json.dumps(r.json()['news'])
        display_date = r.json()['display_date']
        try:
            cursor.execute('INSERT INTO zhihudaily VALUES (?, ?, ?, ?)',
                           (i, date, json_news, display_date))
            db.commit()
        except sqlite3.IntegrityError:  # if the record has been stored before
            pass
        except sqlite3.OperationalError:
            cursor.execute('CREATE TABLE zhihudaily (id integer,\
                                                     date integer primary key,\
                                                     json_news varchar,\
                                                     display_date varchar)'
            )
        except Exception as error:
            print error


if __name__ == '__main__':
    init_database()



