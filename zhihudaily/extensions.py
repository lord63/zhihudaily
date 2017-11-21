#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from raven.contrib.flask import Sentry


# set dsn via SENTRY_DSN in ENV
sentry = Sentry()
