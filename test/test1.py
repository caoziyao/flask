# coding: utf-8


config = {
    'host': '',
    'port': 5000,
    'debug': True,
}


if 'debug' in config:
    debug = config.pop('debug')
    config.setdefault('user', debug)
    a = config.setdefault('user', 'sfw')
    print('a', a)
    print(config)