#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import datetime
import os
from os import path
import sys

import click
import requests
import peewee

from zhihudaily.models import Zhihudaily, create_tables
from zhihudaily.utils import handle_image, get_news_info


class Crawler(object):
    def __init__(self):
        # Zhihudaily's birthday is 20130519, but the url should be
        # http://news.at.zhihu.com/api/1.2/news/before/20130520.
        self.birthday = datetime.date(2013, 5, 20)
        self.today = datetime.date.today()

        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': ("Mozilla/5.0 (X11; Ubuntu; Linux "
                            "x86_64; rv:28.0) Gecko/20100101 Firefox/28.0")})

    def init_database(self, num=10):
        """Init the database and fetch news.

        :param num: int number or string 'all'.
                    the int number stands for the number of days to fetch;
                    string 'all' means fetch all the news start from 20130519.
        """
        print("Init the database...")
        database_path = path.join(path.dirname(path.realpath(__file__)),
                                  'zhihudaily/zhihudaily.db')
        if path.exists(database_path):
            # FIXME: alert before remove the database.
            os.remove(database_path)
        create_tables()

        if num == 'all':
            delta = (self.today - self.birthday).days
        else:
            delta = int(num)
        print('There are {0} records to be fetched.'.format(delta))

        for i in reversed(range(1, delta+1)):
            date = (self.today - datetime.timedelta(i)).strftime("%Y%m%d")
            self._save_to_database(date)
            sys.stdout.write('\rcollect {0} records'.format(delta - i + 1))
            sys.stdout.flush()
        sys.stdout.write('\n')
        print('Init database: done.')

    def daily_update(self):
        """Fetch yestoday's news and save to database."""
        print("Adding yestoday's news to database...")
        yestoday = (self.today - datetime.timedelta(1)).strftime("%Y%m%d")
        self._save_to_database(yestoday)
        print("Update database: done.")
        self.check_integrity()

    def check_integrity(self, date_range=10):
        """Check data integrity, make sure we won't miss a day

        :param date_range: int number or 'all'.
                           the int number means the range of days to check;
                           string 'all' means check data from start 20130519.
        """
        print("Checking date integrity...")
        if isinstance(date_range, int):
            date_in_db = [
                news.date for news in
                (Zhihudaily.select(Zhihudaily.date)
                           .order_by(Zhihudaily.date.desc())
                           .limit(date_range))
            ]
            delta = date_range
        elif date_range == 'all':
            date_in_db = [
                news.date for news in Zhihudaily.select(Zhihudaily.date)
            ]
            delta = (self.today - self.birthday).days
        else:
            raise TypeError("Bad parameter date_range, "
                            "should be an integer or string value 'all'.")

        date_in_real = [
            int((self.today - datetime.timedelta(i)).strftime("%Y%m%d"))
            for i in range(1, delta+1)
        ]
        missed_date = set(date_in_real) - set(date_in_db)
        for date in missed_date:
            print("fetching {0}...".format(date))
            self._save_to_database(str(date))
        print("Check date integrity: done.")

    def _save_to_database(self, given_date):
        """Save news on the specified date to the database.

        :param given_date: strint type, e.g. '20151106'.
        """
        if Zhihudaily.select().where(
                Zhihudaily.date == int(given_date)).exists():
            print('{0} already in our database, skip.'.format(given_date))
            return
        response_json = self._send_request(given_date)
        display_date, date, news_list = get_news_info(response_json)
        zhihudaily = Zhihudaily(date=int(date), display_date=display_date,
                                json_news=handle_image(news_list))
        try:
            zhihudaily.save()
        except Exception as error:
            print(error)

    def _send_request(self, date):
        """Send request to zhihudaily's API server, return the response.

        :param date: strint type, get news on that day, e.g. '20151106'.
        """

        date = int(date)
        date_in_datetime = datetime.date(
            *[date / 10000, date % 10000 / 100, date % 100])
        # Since the API is before/<date>, news on 20130519 should use
        # before/20130520, so we should use the day after it.
        date_after = (
            date_in_datetime + datetime.timedelta(1)).strftime("%Y%m%d")
        response = self.session.get(
            'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(
                date_after))
        # FIXME: exception handle when can't get the json.
        return response


@click.group()
def cli():
    """Simple script to fetch the zhihudaily news.

    \b
    - init database(deault will fetch 10 days' news)
        $ python fetch_date.py init
    - update database(fetch yestoday's news and check data integrity)
        $ python fetch_date.py update
    - check data integrity, make sure we won't miss a day
        $ python fetch_date.py check <number>
    """
    pass


@cli.command()
def init():
    """init database."""
    crawler.init_database()


@cli.command()
def update():
    """fetch yestoday's news."""
    crawler.daily_update()


@cli.command()
@click.argument('date_range', type=int)
def check(date_range):
    """check data integrity."""
    crawler.check_integrity(date_range)


if __name__ == '__main__':
    crawler = Crawler()
    cli()
