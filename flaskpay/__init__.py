#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskpay.utils.json import DecimalEncoder
from config import configs
from flask import g
from flaskpay.utils.create_token import update_token


# 创建可以被外界导入的数据库连接对象
db = SQLAlchemy()

# 创建可以被外界导入的连接到redis数据库的对象
redis_store = None


#  这个是实际创建app的地方
def get_app(config_name):

    app = Flask(__name__)

    # 加载配置
    app.config.from_object(configs[config_name])

    # json转化的设置
    app.json_encoder = DecimalEncoder

    # 创建连接到mysql数据库的对象
    # db = SQLAlchemy(app)
    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    from flaskpay.apps import api
    app.register_blueprint(api)

    # @app.after_request
    # def after_request(param):
    #     print(111111111111111)
    #     if hasattr(g, 'username'):
    #         # 带有用户信息的token，存储时间为30分钟
    #         username = g.username
    #         a = redis_store
    #         redis_token = redis_store.get("token:%s" % username)
    #         token = update_token(redis_token)
    #         param.set_cookie('token', token, 60 * 30)
    #         # 将token值存储在redis中
    #         redis_store.set('token:%s' % username, token, ex=60 * 30)
    #         print(param)
    #     return param

    return app

"""
1.创建mysql数据库对象，并注册到app上去
2.创建redis数据库的连接对象
3.将蓝图注册到app对象中
4.可以将中间件写在这里
"""
