# coding: utf-8

import os
import datetime
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from werkzeug.datastructures import ImmutableDict, Headers
from werkzeug.local import LocalStack, LocalProxy
from werkzeug.utils import cached_property
from werkzeug.wsgi import SharedDataMiddleware

from jinja2 import Environment, FileSystemLoader

from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.contrib.securecookie import SecureCookie
from itertools import chain


class _PackageBoundObject(object):
    pass


class Flask(_PackageBoundObject):

    def __init__(self, import_name):
        pass



    def run(self, host='127.0.0.1', port=5000, **options):
        from werkzeug import run_simple  # 局部导入: 防止 循环导入
        if 'debug' in options:
            self.debug = options.pop('debug')
        options.setdefault('use_reloader', self.debug)
        options.setdefault('use_debugger', self.debug)
        return run_simple(host, port, self, **options)