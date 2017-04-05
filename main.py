# coding: utf-8
# http://werkzeug-docs-cn.readthedocs.io/zh_CN/latest/tutorial.html#step-0-wsgi

import os
import redis
import urlparse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader


class Shortly(object):
    def __init__(self):
        pass

    def dispatch_request(self, request):
        print '3'
        return Response('Hello World!')

    def wsgi_app(self, environ, start_response):
        print '2'
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        print '1'
        return self.wsgi_app(environ, start_response)


def create_app(with_static=True):
    print '0'
    app = Shortly()
    print '4'
    if with_static:
        print '5'
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
        })
    return app


from werkzeug import run_simple # 局部导入: 防止 循环导入
print '6'
mywsgi = create_app()
print '7'
run_simple('127.0.0.1', 5000, mywsgi, use_debugger=True, use_reloader=True)