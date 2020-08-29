#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


class SentryWrapper(object):
    def init_app(self, app):
        sentry_dsn = os.environ.get("ZHIHUDAILY_SENTRY_DSN")
        if sentry_dsn:
            sentry_sdk.init(sentry_dsn,integrations=[FlaskIntegration()])


sentry_wrapper = SentryWrapper()
