#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
from sqlalchemy.sql import func
from . import api
from flask import request
import datetime
from flaskpay import db
from flaskpay.models import TOrderHis, TPayInfo, TOrder
from flaskpay.utils.restful import data_return, server_error, params_error, result


# 历史订单列表展示
@api.route('/config/order/listOrderHis')
def get_orderhis_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    start_time = request.args.get('startTime', '')
    end_time = request.args.get('endTime', '')
    order_state = request.args.get('orderState', '')
    key = request.args.get('key', '')  # 用户名，订单编号，操作人
    if order_state == '':
        order_state = 30
    try:
        page_int = int(page)
        limit_int = int(limit)
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else datetime.datetime.now()
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") if start_time else datetime.datetime.strptime("1971-01-01 18:55:23", "%Y-%m-%d %H:%M:%S")
        values = db.session.query(TOrderHis, TPayInfo.payment_name, TPayInfo.item_name).join(TPayInfo, TOrderHis.payment_code == TPayInfo.payment_code).filter(TOrderHis.pay_code == TPayInfo.pay_code, TOrderHis.user_account.contains(key) | TOrderHis.order_id.contains(key) | TOrderHis.update_user.contains(key),TOrderHis.order_state == order_state,TOrderHis.order_time >= start_time,TOrderHis.order_time <= end_time).paginate(page_int,limit_int)
        sums = db.session.query(func.sum(TOrderHis.order_amount), func.sum(TOrderHis.rate_amount)).join(TPayInfo, TOrderHis.payment_code == TPayInfo.payment_code).filter(TOrderHis.pay_code == TPayInfo.pay_code,TOrderHis.user_account.contains(key) | TOrderHis.order_id.contains(key) | TOrderHis.update_user.contains(key),TOrderHis.order_state == order_state,TOrderHis.order_time <= end_time).all()
        data_list = []
        responseData = {
            "allMoney": sums[0][0],
            "allPoundage": sums[0][1]
        }
        items = values.items
        count = values.total
        for item in items:
            data_dict = item.TOrderHis.to_full_dict()
            data_dict["payName"] = item.item_name
            data_dict["paymentName"] = item.payment_name
            data_list.append(data_dict)
        return data_return(data=data_list, kwargs={"count": count, "responseData": responseData})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 订单列表展示
@api.route('/config/order/ordergrid')
def get_order_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    start_time = request.args.get('startTime', '')
    end_time = request.args.get('endTime', '')
    key = request.args.get('key', '')  # 用户名，订单编号，操作人
    order_state = request.args.get('orderState', '')
    payment_code = request.args.get('paymentCode', '')  # 平台名称
    try:
        page_int = int(page)
        limit_int = int(limit)
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else datetime.datetime.now()
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") if start_time else datetime.datetime.strptime("1971-01-01 18:55:23", "%Y-%m-%d %H:%M:%S")
        if order_state == '':
            values = db.session.query(TOrder, TPayInfo.payment_name, TPayInfo.item_name).join(TPayInfo, TOrder.payment_code == TPayInfo.payment_code).filter(TOrder.pay_code == TPayInfo.pay_code,TOrder.user_account.contains(key) | TOrder.order_id.contains(key) | TOrder.update_user.contains(key),TOrder.order_time >= start_time,TOrder.order_time <= end_time,TOrder.payment_code.startswith(payment_code)).paginate(page_int, limit_int)
        else:
            values = db.session.query(TOrder, TPayInfo.payment_name, TPayInfo.item_name).join(TPayInfo,TOrder.payment_code == TPayInfo.payment_code).filter(TOrder.pay_code == TPayInfo.pay_code, TOrder.user_account.contains(key) | TOrder.order_id.contains(key) | TOrder.update_user.contains(key), TOrder.order_state == order_state, TOrder.order_time >= start_time, TOrder.order_time <= end_time, TOrder.payment_code.startswith(payment_code)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        data_list = []
        for item in items:
            data_dict = item.TOrder.to_full_dict()
            data_dict["payName"] = item.item_name
            data_dict["paymentName"] = item.payment_name
            data_list.append(data_dict)
        return data_return(data=data_list, kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 统计订单的总金额
@api.route('/config/order/orderSum')
def get_order_sum():
    start_time = request.args.get('startTime', '')
    end_time = request.args.get('endTime', '')
    key = request.args.get('key', '')  # 用户名，订单编号，操作人
    order_state = request.args.get('orderState', '')
    payment_code = request.args.get('paymentCode', '')  # 平台名称
    try:
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else datetime.datetime.now()
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") if start_time else datetime.datetime.strptime("1971-01-01 18:55:23", "%Y-%m-%d %H:%M:%S")
        if order_state == '':
            sums = db.session.query(func.sum(TOrder.order_amount), func.sum(TOrder.rate_amount)).join(TPayInfo, TOrder.payment_code == TPayInfo.payment_code).filter(TOrder.pay_code == TPayInfo.pay_code,TOrder.user_account.contains(key) | TOrder.order_id.contains(key) | TOrder.update_user.contains(key),TOrder.order_time >= start_time,TOrder.order_time <= end_time,TOrder.payment_code.startswith(payment_code)).all()
        else:
            sums = db.session.query(func.sum(TOrder.order_amount), func.sum(TOrder.rate_amount)).join(TPayInfo, TOrder.payment_code == TPayInfo.payment_code).filter(TOrder.pay_code == TPayInfo.pay_code,TOrder.user_account.contains(key) | TOrder.order_id.contains(key) | TOrder.update_user.contains(key),TOrder.order_time >= start_time,TOrder.order_time <= end_time,TOrder.payment_code.startswith(payment_code),TOrder.order_state == order_state).all()
        responseData = {
            "allMoney": sums[0][0] if sums[0][0] else 0,
            "allPoundage": sums[0][1] if sums[0][1] else 0
        }
        return data_return(kwargs={"responseData": responseData})
    except Exception as e:
        return params_error(message='参数传递有误，请重试！')


# 待处理订单展示
@api.route('/config/order/tobegrid')
def get_order_tobe_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    order_state = request.args.get('orderState', '')
    key = request.args.get('key', '')  # 用户名，订单编号，操作人
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = db.session.query(TOrder, TPayInfo.payment_name, TPayInfo.item_name).join(TPayInfo, TOrder.payment_code == TPayInfo.payment_code).filter(TOrder.pay_code == TPayInfo.pay_code,TOrder.user_account.contains(key) | TOrder.order_id.contains(key) | TOrder.update_user.contains(key),TOrder.order_state == order_state, TOrder.state == 10).paginate(page_int, limit_int)
        sums = db.session.query(func.sum(TOrder.order_amount), func.sum(TOrder.rate_amount)).join(TPayInfo, TOrder.payment_code == TPayInfo.payment_code).filter(TOrder.pay_code == TPayInfo.pay_code,TOrder.user_account.contains(key) | TOrder.order_id.contains(key) | TOrder.update_user.contains(key),TOrder.order_state == order_state, TOrder.state == 10).all()
        items = values.items
        count = values.total
        data_list = []
        responseData = {
            "allMoney": sums[0][0] if sums[0][0] else 0,
            "allPoundage": sums[0][1] if sums[0][1] else 0
        }
        for item in items:
            data_dict = item.TOrder.to_full_dict()
            data_dict["payName"] = item.item_name
            data_dict["paymentName"] = item.payment_name
            data_list.append(data_dict)
        return data_return(data=data_list, kwargs={"count": count, "responseData": responseData})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 锁定待处理订单
@api.route('/config/order/lockOrder/<int:id>', methods=['POST'])
def set_lock_order(id):
    user = 'admin'
    try:
        value = TOrder.query.get(id)
        value.update_user = user
        value.update_time = datetime.datetime.now()
        value.state = 20
        value.lock_id = user
        db.session.commit()
        return result(message="修改成功")
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 我的订单信息展示
@api.route('/config/order/myOrder')
def get_myorder_list():
    start_time = request.args.get('startTime', '')
    end_time = request.args.get('endTime', '')
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    order_state = request.args.get('orderState', '')
    key = request.args.get('key', '')  # 用户名，订单编号
    user = 'admin'
    if order_state == '':
        order_state = 30
    try:
        page_int = int(page)
        limit_int = int(limit)
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else datetime.datetime.now()
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") if start_time else datetime.datetime.strptime("1971-01-01 18:55:23", "%Y-%m-%d %H:%M:%S")
        values = db.session.query(TOrder, TPayInfo.payment_name, TPayInfo.item_name).join(TPayInfo, TOrder.payment_code == TPayInfo.payment_code).filter(TOrder.pay_code == TPayInfo.pay_code, TOrder.user_account.contains(key) | TOrder.order_id.contains(key),TOrder.order_state == order_state, TOrder.update_user == user, TOrder.state != 10,TOrder.update_time >= start_time, TOrder.update_time <= end_time).paginate(page_int, limit_int)
        sums = db.session.query(func.sum(TOrder.order_amount), func.sum(TOrder.rate_amount)).join(TPayInfo, TOrder.payment_code == TPayInfo.payment_code).filter(TOrder.pay_code == TPayInfo.pay_code, TOrder.user_account.contains(key) | TOrder.order_id.contains(key),TOrder.order_state == order_state, TOrder.update_user == user, TOrder.state != 10,TOrder.update_time >= start_time, TOrder.update_time <= end_time).all()
        items = values.items
        count = values.total
        data_list = []
        responseData = {
            "allMoney": sums[0][0] if sums[0][0] else 0,
            "allPoundage": sums[0][1] if sums[0][1] else 0
        }
        for item in items:
            data_dict = item.TOrder.to_full_dict()
            data_dict["payName"] = item.item_name
            data_dict["paymentName"] = item.payment_name
            data_list.append(data_dict)
        return data_return(data=data_list, kwargs={"count": count, "responseData": responseData})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 解锁，我的订单
@api.route('/config/order/updateMyOrder/<int:id>', methods=['POST'])
def update_order(id):
    state = request.form.get('state', None)
    order_desc = request.form.get('orderDesc', None)
    order_state = request.form.get('orderState', None)
    if state == '50':
        state = '10'
    try:
        value = TOrder.query.get(id)
        value.state = state
        value.order_desc = order_desc
        value.lock_id = 0
        db.session.commit()
        return result(message="修改成功")
    except Exception as e:
        return server_error(message="查找失败，请重试")
