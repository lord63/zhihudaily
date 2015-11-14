#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import os

from flask_script import Manager

from zhihudaily.app import create_app
from zhihudaily.configs import DevelopConfig, ProductionConfig


if os.environ.get('Flask_APP') == 'production':
    app = create_app(ProductionConfig)
else:
    app = create_app(DevelopConfig)

manager = Manager(app)


if __name__ == '__main__':
    manager.run()
