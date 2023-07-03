#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
import logging
import datetime


class Config(object):
    DEBUG = True
    SECRET_KEY = 'AK0j4NSomJQKm8gD/917OniOIC8DEMQRP+xPBvGanEBieaADMBTA0EBTrJdAiXgU'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/carea_pay1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@192.168.72.77:3306/carea_pay'


configs = {
    'default_config': Config,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
