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
@click.argument('date_range')
def check(date_range):
    """check data integrity."""
    crawler.check_integrity(date_range)


if __name__ == '__main__':
    crawler = Crawler()
    cli()
