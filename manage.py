#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

import click

from zhihudaily.crawler import Crawler
from zhihudaily.app import create_app
from zhihudaily.configs import DevelopConfig, ProductionConfig


CONFIG = (ProductionConfig if os.environ.get('FLASK_APP_ENV') == 'production'
          else DevelopConfig)
app = create_app(CONFIG)
crawler = Crawler()


@app.cli.command()
@click.option('--num', '-n', default=10)
@click.option('--all', is_flag=True)
def init_db(num, all):
    """init database.

    \b
    :param num: int, the number of daily news to fetch.
    :param all: boolean, fetch all the news or not.
    """
    if all:
        crawler.init_database('all')
    else:
        crawler.init_database(num)


@app.cli.command()
def update_news():
    """Fetch today's latest news and save to database."""
    crawler.daily_update()


@app.cli.command()
@click.option('--range', '-r', default=10)
@click.option('--all', is_flag=True)
def check_news(range, all):
    """check data integrity.

    \b
    :param range: int, the range of days to check
    :param all: boolean, check all the data integrity or not.
    """
    if all:
        crawler.check_integrity('all')
    else:
        crawler.check_integrity(range)