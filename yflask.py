"""
flask: 微型web框架.
    - 核心依赖:
        - Werkzeug :
            - 功能实现: request, response
            - 导入接口: 部分未实现接口, 直接导入用
        - jinja2 :
            - 功能实现:
            - 导入接口: 模板

    - 核心功能模块:
        - Request()    # 未实现,借用自 Werkzeug
        - Response()   # 未实现,借用自 Werkzeug
        - Flask()      # 核心功能类
"""

from __future__ import with_statement
import os
import sys

from threading import local

from jinja2 import (        # flask 部分模块实现,依赖 jinja2
    Environment,
    PackageLoader,
    FileSystemLoader
)

# 说明:
#   - flask 部分模块实现,严重依赖 werkzeug
#   - werkzeug 最新版本,模块组织结构发生改变.
#   - 故替换部分失效导包语句,请注意
#   - 下面最后一条导包语句,已失效, 暂未找到有效的替换
#
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase    # 关键依赖
from werkzeug.local import LocalStack, LocalProxy     # 文件末尾, _request_ctx_stack, current_app 中依赖
from werkzeug.wsgi import SharedDataMiddleware        # Flask() 模块 中引用
from werkzeug.utils import cached_property
from werkzeug import create_environ    # 已失效

from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.contrib.securecookie import SecureCookie

from werkzeug import abort, redirect      # werkzeug 依赖: 本文件未使用,但导入以用作 对外接口
from jinja2 import Markup, escape         # jinja2 的依赖: 本文件未使用,但导入以用作 对外接口

try:
    import pkg_resources
    pkg_resources.resource_stream
except (ImportError, AttributeError):
    pkg_resources = None


# from werkzeug.wrappers import Request, Response

def _get_package_path(name):     # 获取 模块包 路径, Flask() 中 引用
    """Returns the path to a package or cwd if that cannot be found."""
    try:
        return os.path.abspath(os.path.dirname(sys.modules[name].__file__))
    except (KeyError, AttributeError):
        return os.getcwd()




class Flask(object):
    """
    自定义flask
    """
    static_path = '/static'                  # 静态资源路径
    # request_class = Request      # 请求类
    # # response_class = Response    # 响应类

    def __init__(self, package_name):
        self.package_name = package_name
        self.view_function = {}             # 视图函数集
        self.debug = False
        self.before_request_funcs = []     # 预处理

        # 获取 模块包 路径, Flask() 中 引用
        self.root_path = _get_package_path(self.package_name)

        # todo: 待深入
        self.url_map = Map()    # 关键依赖: werkzeug.routing.Map

    # 返回响应
    def make_response(self, rv):
        """Converts the return value from a view function to a real
        """
        pass
        

    # 对外运行接口: 借用werkzeug.run_simple 实现
    def run(self, host='localhost',  port=5000, **options):
        """ Runs the application on a local development server.
        """
        from werkzeug import run_simple    # todo: 待深入, 关键依赖: 核心运行模块
        return run_simple(host, port, self, **options)    # 关键依赖:


    # todo: 待深入, 对外接口:
    def wsgi_app(self, environ, start_response):
        response = ResponseBase('Hello World!', mimetype='text/plain')
        return response(environ, start_response)


    # todo: 待深入, 关键依赖。run_simple 调用
    def __call__(self, environ, start_response):
        """Shortcut for :attr:`wsgi_app`"""
        return self.wsgi_app(environ, start_response)
        


    # 关键接口: 创建 or 打开一个 会话(session)
    #   - 实现方式: 使用 cookie 实现
    #   - 默认把全部session数据, 存入一个 cookie 中.
    #   - 对比 flask-0.4 版本, 部分重构
    #
    def open_session(self, request):
        """Creates or opens a new session.
        Default implementation stores all session data in a signed cookie.
        This requires that the :attr:`secret_key` is set.

        :param request: an instance of :attr:`request_class`.
        """
        pass
        # key = self.secret_key
        # if key is not None:
        #     return SecureCookie.load_cookie(request, self.session_cookie_name,
        #                                     secret_key=key)
    
    def route(self, route, **options):
        """
        @app.route('/')
        def index():
            return 'Hello World'

        @app.route('/<username>')
        def show_user(username):
            pass

        @app.route('/post/<int:post_id>')
        def show_post(post_id):
            pass
        """

        def decorator(f):
            self.view_function[f.__name__] = f
            return f
        return decorator


