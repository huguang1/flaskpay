#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
from flask import Blueprint

# 提示：一个借口版本里面需要一个蓝图，并指定版本唯一标识
api = Blueprint('apps', __name__, url_prefix='/')

# 为了让导入api蓝图时，蓝图注册路由的代码可以跟着被导入，那么我们的路由和视图对应关系中就会有路由
from . import cfg, order, pay, system


"""
1.这里就是将蓝图注册，防止重复导入
"""
