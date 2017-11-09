#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

import click

from zhihudaily.app import create_app
from zhihudaily.configs import DevelopConfig, ProductionConfig



CONFIG = (ProductionConfig if os.environ.get('FLASK_APP_ENV') == 'production'
          else DevelopConfig)
app = create_app(CONFIG)