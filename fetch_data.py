#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import click

from zhihudaily.crawler import Crawler


@click.group()
def cli():
    """Simple script to fetch the zhihudaily news.

    \b
    - init database(deault will fetch 10 days' news)
        $ python fetch_date.py init
    - update database(fetch today's latest news and check data integrity)
        $ python fetch_date.py update
    - check data integrity, make sure we won't miss a day(default check 10 days)
        $ python fetch_date.py check

    get more detailed info for each subcommand via <subcommand --help>
    """
    pass


@cli.command()
@click.option('--num', '-n', default=10)
@click.option('--all', is_flag=True)
def init(num, all):
    """init database.

    :param num: int, the number of daily news to fetch.
    :param all: boolean, fetch all the news or not.
    """
    if all:
        crawler.init_database('all')
    crawler.init_database(num)


@cli.command()
def update():
    """Fetch today's latest news and save to database."""
    crawler.daily_update()


@cli.command()
@click.option('--range', '-r', default=10)
@click.option('--all', is_flag=True)
def check(range, all):
    """check data integrity.

    :param range: int, the range of days to check
    :param all: boolean, check all the data integrity or not.
    """
    if all:
        crawler.check_integrity('all')
    crawler.check_integrity(range)


if __name__ == '__main__':
    crawler = Crawler()
    cli()
