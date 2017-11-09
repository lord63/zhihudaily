# -*- coding: utf-8 -*-
"""
    flask._compat
    ~~~~~~~~~~~~~
    Some py2/py3 compatibility support based on a stripped down
    version of six so we don't have to depend on a specific version
    of it.
    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import sys

PY2 = sys.version_info[0] == 2

if not PY2:
    from io import StringIO
    from urllib.parse import urljoin
else:
    from cStringIO import StringIO
    from urlparse import urljoin