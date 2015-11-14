#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime
import json
import os
from os import path
import re
import sys

import click
import requests

from zhihudaily.models import Zhihudaily, create_tables
from zhihudaily.configs import Config


def handle_image(news_list):
    """Point all the images to my server, because use zhihudaily's
    images directly may get 403 error.
    """
    for news in news_list:
        items = re.search(r'(?<=http://)(.*?)\.zhimg.com/(.*)$', news['image'])
        if items is None:
            continue
        news['image'] = (
            'http://zhihudaily.lord63.com/img/{0}/{1}'.format(*items.groups()))
    return news_list


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
        click.echo("Init the database...")
        if path.exists(Config.db):
            confirm = click.prompt(
                "Already exists a database, continue by removing it? [Y/n]",
                default='Y', show_default=False)
            if confirm == 'Y':
                os.remove(Config.db)
            else:
                sys.exit('Keep the database and abort.')
        create_tables()

        if num == 'all':
            delta = (self.today - self.birthday).days
        else:
            delta = int(num)
        click.echo('There are {0} records to be fetched.'.format(delta))

        for i in reversed(range(delta)):
            date = (self.today - datetime.timedelta(i)).strftime("%Y%m%d")
            self._save_to_database(date)
            sys.stdout.write('\r    collect {0} records'.format(delta - i))
            sys.stdout.flush()
        sys.stdout.write('\n')
        self.check_integrity(num)
        click.echo('Init database: done.')

    def daily_update(self):
        """Fetch today's latest news and save to database."""
        click.echo("Update today's news in database...")
        self._save_to_database(self.today.strftime("%Y%m%d"))
        click.echo("Update database: done.")
        self.check_integrity()

    def check_integrity(self, date_range=10):
        """Check data integrity, make sure we won't miss a day

        :param date_range: int number or 'all'.
                           the int number means the range of days to check;
                           string 'all' means check data from start 20130519.
        """
        click.echo("Checking date integrity...")
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
            for i in range(delta)
        ]
        missed_date = set(date_in_real) - set(date_in_db)
        for date in missed_date:
            click.echo("    fetching {0}...".format(date))
            self._save_to_database(str(date))
        click.echo("Check data integrity: done.")

    def _save_to_database(self, given_date):
        """Save news on the specified date to the database.

        :param given_date: string type, e.g. '20151106'.
        """
        response = self._send_request(given_date)
        if response is None:
            return

        if Zhihudaily.select().where(
                Zhihudaily.date == int(given_date)).exists():
            zhihudaily = Zhihudaily.get(Zhihudaily.date == int(given_date))
            zhihudaily.json_news = json.dumps(
                handle_image(response.json()['news']))
        else:
            zhihudaily = Zhihudaily(
                date=int(response.json()['date']),
                display_date=response.json()['display_date'],
                json_news=json.dumps(handle_image(response.json()['news']))
            )
        try:
            zhihudaily.save()
        except Exception as error:
            click.echo("Fail to save to database: {0}".format(error.args[0]))

    def _send_request(self, date):
        """Send request to zhihudaily's API server, return the response.

        :param date: strint type, get news on that day, e.g. '20151106'.
        """

        date_in_datetime = datetime.date(
            int(date[0:4]), int(date[4:6]), int(date[6:8]))
        # Since the API is before/<date>, news on 20130519 should use
        # before/20130520, so we should use the day after it.
        date_after = (
            date_in_datetime + datetime.timedelta(1)).strftime("%Y%m%d")
        try:
            response = self.session.get(
                'http://news.at.zhihu.com/api/1.2/news/before/{0}'.format(
                    date_after))
        except requests.exceptions.RequestException as error:
            click.echo("Fail to send the request: {0}".format(error.args[0]))
            return None
        else:
            return response


@click.group()
def cli():
    """Simple script to fetch the zhihudaily news.

    \b
    - init database(deault will fetch 10 days' news)
        $ python fetch_date.py init
    - update database(fetch today's latest news and check data integrity)
        $ python fetch_date.py update
    - check data integrity, make sure we won't miss a day
        $ python fetch_date.py check <number>

    get more detailed info for each subcommand via <subcommand --help>
    """
    pass


@cli.command()
@click.option('--num', '-n', default=10)
def init(num):
    """init database."""
    crawler.init_database(num)


@cli.command()
def update():
    """Fetch today's latest news and save to database."""
    crawler.daily_update()


@cli.command()
@click.argument('date_range', type=int)
def check(date_range):
    """check data integrity."""
    crawler.check_integrity(date_range)


if __name__ == '__main__':
    crawler = Crawler()
    cli()
