#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
from functools import wraps
from flask import session, g, request
from flaskpay.utils.restful import server_error, params_error
from flaskpay import redis_store
from flask import g
from flaskpay.utils.create_token import update_token


def login_required(view_func):
    """校验用户是否是登录用户"""
    # 装饰器装饰一个函数时，会修改该函数的__name__属性
    # 如果希望装饰器装饰之后的函数，依然保留原始的名字和说明文档,就需要使用wraps装饰器，装饰内存函数
    @wraps(view_func)
    def wraaper(*args, **kwargs):
        # 获取到用户session中的用户名
        username = session.get('username')
        # 用户名过期
        if not username:
            return server_error(message='用户未登录')
        else:
            # 表示用户已登录，使用g变量保存住user_id,方便在view_func调用的时候，内部可以直接使用g变量里面的username
            g.username = username
            headerToken = request.headers["X-CSRF-TOKEN"]
            redis_token = redis_store.get("token:%s" % username)
            if not redis_token or str(redis_token, encoding="utf-8") != headerToken:
                return params_error(message="CSRF校验不能通过，请重试！")
            redis_token = redis_store.get("token:%s" % username)
            token = update_token(redis_token)
            response = view_func(*args, **kwargs)
            response.set_cookie('token', token, 60 * 30)
            # 将token值存储在redis中
            redis_store.set('token:%s' % username, token, ex=60 * 30)
            return response
    return wraaper

"""
1.装饰器，既可以实现对函数之前进行操作，也可以对函数之后进行操作
"""
