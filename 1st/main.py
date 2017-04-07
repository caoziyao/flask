# coding:utf-8

from yflask import Flask

app = Flask(__name__)


config = {
    'host': '',
    'port': 5000,
    'debug': True,
}

app.run(**config)