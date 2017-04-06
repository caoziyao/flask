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




class Flask():

    def __init__(self):
        