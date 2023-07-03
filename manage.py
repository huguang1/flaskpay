#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
from flaskpay import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flaskpay import get_app
from flaskpay import models  # 在迁移之前，将模型导入一下，为了保证脚本知道模型文件的存在。没有实际的意义
from datetime import timedelta

# 创建app
app = get_app("development")

# 创建脚本管理器对象
manager = Manager(app)

# 让app和db在迁移时建立关联
Migrate(app, db)

# 将数据库迁移脚本添加到脚本管理器
manager.add_command("db", MigrateCommand)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)


if __name__ == '__main__':
    manager.run()

"""
1.导入app对象
2.将数据库脚本绑定在app上
3.启动app服务器
"""
