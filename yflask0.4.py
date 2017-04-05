# coding: utf-8
# https://segmentfault.com/a/1190000004223296
# http://www.jianshu.com/p/7a7efbb7205f

import os
from werkzeug.wrappers import Request as RequestBase, Response as ResponseBase
from werkzeug.datastructures import ImmutableDict, Headers
from werkzeug.local import LocalStack, LocalProxy
from werkzeug.utils import cached_property
from werkzeug.wsgi import SharedDataMiddleware

from jinja2 import Environment, FileSystemLoader

from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.contrib.securecookie import SecureCookie


class ConfigAttribute(object):
    def __init__(self, name):
        self.__name__ = name


class Response(ResponseBase):
    """"""
    default_mimetype = 'text/html'


class Request(RequestBase):

    endpoint = None
    view_args = None
    routing_exception = None
    # endpoint = view_args = routing_exception = None

    @property
    def module(self):
        """The name of the current module"""
        if self.endpoint and '.' in self.endpoint:
            return self.endpoint.rsplit('.', 1)[0]


class Session():
    pass


class _RequestGlobals(object):
    pass



# 特别注意:
#   - 深入理解 "上下文概念"
#   - 支持多线程, 线程无关

###################################################################
#                  请求上下文定义部分
#
# 说明:
#   - 超级关键, 非常重要
#   - 内部实现 请求上下文的 g, session
#   - flask.request_context() 中 引用
#
###################################################################
class _RequestContext(object):
    # flask 通过 _RequestContex 将 app 与 Request 关联起来
    def __init__(self, app, environ):
        # 指的就是当你调用app = Flask(__name__)创建的这个对象app；
        # 由同一个Flask对象响应的请求所创建的_RequestContext对象的app成员变量都共享同一个application
        # 实现了多个request context对应一个application context 的目的。
        self.app = app
        self.url_adapter = app.url_map.bind_to_environ(environ)
        print 'app', self.app
        # request 指的是每次http请求发生时，WSGI server(比如gunicorn)调用Flask.__call__()之后，在Flask对象内部创建的Request对象；
        # 实际上是创建了一个Request对象
        # 每个http请求对应一个Request对象
        self.request = app.request_class(environ)
        print 'request', self.request
        # 会话(session) 实现:
        self.session = app.open_session(self.request)  # 关键代码:  session: 请求上下文的 session 对象
        print 'session', self.session
        # g 实现:
        self.g = _RequestGlobals()  # g: 请求上下文的 g 对象
        print 'g', self.g

        try:
            self.request.endpoint, self.request.view_args =  self.url_adapter.match()
        except Exception, e:
            self.request.routing_exception = e
#
    # 入栈:
    #   - 绑定 请求上下文
    #   - 把 自身所有变量, 入栈 --> 实现带上下文的 g, session
    #
    def push(self):
        """Binds the request context."""
        _request_ctx_stack.push(self)  # 全局对象: 文件末尾定义
    #
    # 出栈:
    #   - 输出 请求上下文
    #
    def pop(self):
        """Pops the request context."""
        _request_ctx_stack.pop()  # 全局对象: 文件末尾定义

    def __enter__(self):
        self.push()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop()  # 自动 出栈


def render_template(template_name, **context):
    # yflask
    template_path = os.path.join(os.path.dirname(__file__), 'template')
    jinja_env = Environment(loader=FileSystemLoader(template_path),
                                 autoescape=True)

    t = jinja_env.get_template(template_name)
    return Response(t.render(context), mimetype='text/html')



# core flask
class Flask():
    request_class = Request
    response_class = Response
    static_path = '/static'

    testing = ConfigAttribute('TESTING')
    debug = ConfigAttribute('DEBUG')
    secret_key = ConfigAttribute('SECRET_KEY')
    session_cookie_name = ConfigAttribute('SESSION_COOKIE_NAME')
    permanent_session_lifetime = ConfigAttribute('PERMANENT_SESSION_LIFETIME')
    use_x_sendfile = ConfigAttribute('USE_X_SENDFILE')
    logger_name = ConfigAttribute('LOGGER_NAME')

    debug_log_format = ()
    jinja_option = ()
    default_config = ()

    # def dispatch_request(self, request):
    #     return ResponseBase('Hello flask!')


    #
    # 关键接口: 请求上下文
    #
    def request_context(self, environ):
        """ 入口: 请求上下文 """
        return _RequestContext(self, environ)  # 关键类

    # 请求预处理
    #   - 在每次请求处理前, 被调用
    def preprocess_request(self, environ):
        """ wsgi_app 调用
        1. preprocess_request
        2. make_response
        3. process_response
        """
        # request = RequestBase(environ)

        return None

    def make_response(self, rv):
        """ wsgi_app 调用
        1. preprocess_request
        2. make_response
        3. process_response
        """
        if isinstance(rv, self.response_class):
            return rv

    def process_response(self, response):
        """ wsgi_app 调用
        1. preprocess_request
        2. make_response
        3. process_response
        """
        return response

    def dispatch_request(self):
        req = _request_ctx_stack.top.request
        # req.endpoint 路由函数key, script.scroptsplit
        # req.view_args 参数 {'sid': 125}
        return self.view_functions[req.endpoint](**req.view_args)
        # view_functions 路由函数
        # return self.view_functions['index']()


    def wsgi_app(self, environ, start_response):
        print 'environ', environ  # headers 等内容信息
        print  'start_response', start_response  # 函数

        # 在Flask类中，每次请求都会调用这个request_context函数。这个函数则会创建一个_RequestContext对象。
        with self.request_context(environ):   # 入口: 请求上下文

            rv = self.preprocess_request(environ)  # 获取请求(request)
            if rv is None:
                rv = self.dispatch_request()
            response = self.make_response(rv)  # 处理, 并生成 响应
            response = self.process_response(response)  # 返回响应(response)

            return response(environ, start_response)  # 出口: 返回响应

    def __call__(self, environ, start_response):
        """Shortcut for :attr:`wsgi_app`."""
        return self.wsgi_app(environ, start_response)

    def __init__(self):

        self.before_request_funcs = {}
        self.url_map = Map()

        self.view_functions = {}

        target = os.path.join(os.path.dirname(__file__), 'static')  # static 文件路径

        self.wsgi_app = SharedDataMiddleware(self.wsgi_app, {
            self.static_path: target
        })


    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        if endpoint is None:
            endpoint = view_func.__name__
        options['endpoint'] = endpoint
        options.setdefault('methods', ('GET',))
        self.url_map.add(Rule(rule, **options))     # 添加路由
        if view_func is not None:
            self.view_functions[endpoint] = view_func  # 视图函数集合

    #
    # 关键接口: 路由装饰器
    # @app.route('/')
    # def index():
    #     return 'Hello World'
    #
    def route(self, rule, **options):
        def decorator(f):
            self.add_url_rule(rule, None, f, **options)
            return f
        return decorator

    def before_request(self, f):

        return f

    #
    # 关键接口: 创建 or 打开一个 会话(session)
    #   - 实现方式: 使用 cookie 实现
    #   - 默认把全部session数据, 存入一个 cookie 中.
    #
    def open_session(self, request):
        return ''

    def run(self, host='127.0.0.1', port=5000, **options):
        from werkzeug import run_simple  # 局部导入: 防止
        # 浏览器请求的时候，就会调用 Flask实例，实际上是调用了 __call__ 方法
        return run_simple(host, port, self, **options)

###################################################################
#               全局变量 定义部分
# 说明:
#   - 关键部分
#   - 请求上下文对象
#   - 全局对象
#
###################################################################


# context locals
_request_ctx_stack = LocalStack()


#
# 应用级上下文:
#   - 应用级别: 数据隔离
#   - 多个app之间(app1, app2), 数据是相互隔离的
#
current_app = LocalProxy(lambda: _request_ctx_stack.top.app)  # 应用上下文: current_app
g = LocalProxy(lambda: _request_ctx_stack.top.g)              # 应用上下文: g 对象

#
# 请求级上下文:
#   - 请求级别: 数据隔离
#   - 多个请求之间, 数据是隔离开的
#
request = LocalProxy(lambda: _request_ctx_stack.top.request)  # 请求上下文: request
session = LocalProxy(lambda: _request_ctx_stack.top.session)  # 请求上下文: 会话(session)


###################

app = Flask()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


app.run()


