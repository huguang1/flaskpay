#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
from . import api
from flask import request
from flaskpay.models import TGroup, TPayInfo, TCustomerUser
from flaskpay import db
import json
from flaskpay.utils.restful import data_return, server_error, result


# 会员分级展示
@api.route('/config/group/groupList')
def get_group_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = TGroup.query.filter().paginate(page_int, limit_int)
        items = values.items
        count = values.total
        data_list = []
        for item in items:
            value_dict = item.to_full_dict()
            if item.str_values:
                item.str_values = json.loads(item.str_values)
                for key, dic in item.str_values.items():
                    value_dict[key] = dic.split('&')[1]
            data_list.append(value_dict)
        return data_return(data=data_list, kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找会员分级所有信息失败，请重试")


# 增加会员分级
@api.route('/config/group/save', methods=['POST'])
def create_group():
    name = request.form.get('name', None)
    try:
        tg = TGroup(name=name)
        db.session.add(tg)
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 删除会员分级
@api.route('/config/group/del/<int:id>', methods=['POST'])
def delete_group(id):
    try:
        td = TGroup.query.get(id)
        db.session.delete(td)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 查看一个会员分级
@api.route('/config/group/find/<int:id>')
def get_group_find(id):
    try:
        tli = TGroup.query.get(id)
        group = {
            "id": tli.id,
            "name": tli.name
        }
        if tli.str_values:
            tli.str_values = json.loads(tli.str_values)
            for key, dic in tli.str_values.items():
                group[key] = dic
        return data_return(data=group)
    except Exception as e:
        return server_error(message="获取失败，请重试")


# 获取到所有的支付通道的信息
@api.route('/config/group/available')
def get_group_available():
    try:
        values = TPayInfo.query.filter().all()
        count = len(values)
        return data_return(data=[value.to_full_dict() for value in values], kwargs={"count": count})
    except Exception as e:
        return server_error(message="获取失败，请重试")


# 修改支付通道
@api.route('/config/group/upd/<int:id>', methods=['POST'])
def update_group(id):
    name = request.form.get('name', None)
    str_list = request.form.get('strValues', '').split(',')
    str_values = {}
    for str_value in str_list:
        str_values[str_value.split('&')[0]] = str_value
    str_values = json.dumps(str_values)
    try:
        tg = TGroup.query.get(id)
        tg.name = name
        tg.str_values = str_values
        db.session.commit()
        return result(message="更改成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 获取所有的会员等级
@api.route('/config/group/box')
def get_group_box():
    try:
        values = TGroup.query.filter().all()
        count = len(values)
        return result(data=[value.to_full_dict() for value in values], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找会员分级所有信息失败，请重试")


# 会员列表展示
@api.route('/config/customer/customerList')
def get_customer_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    group_id = request.args.get('groupId', '')
    user_account = request.args.get('userAccount', '')
    try:
        page_int = int(page)
        limit_int = int(limit)
        if group_id == '':
            values = db.session.query(TCustomerUser, TGroup.name).join(TGroup, TCustomerUser.group_id == TGroup.id).filter(TCustomerUser.user_account.contains(user_account)).paginate(page_int, limit_int)
        else:
            values = db.session.query(TCustomerUser, TGroup.name).join(TGroup, TCustomerUser.group_id == TGroup.id).filter(TCustomerUser.group_id == group_id, TCustomerUser.user_account.contains(user_account)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        data_list = []
        for item in items:
            data_dict = item.TCustomerUser.to_full_dict()
            data_dict["groupName"] = item.name
            data_list.append(data_dict)
        return data_return(data=data_list, kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找会员分级所有信息失败，请重试")


# 添加会员
@api.route('/config/customer/save', methods=['POST'])
def create_customer():
    id = request.form.get('id', None)
    user_account = request.form.get('userAccount', None)
    group_id = request.form.get('groupId', None)
    try:
        if id:
            tcu = TCustomerUser.query.get(id)
            tcu.user_account = user_account
            tcu.group_id = group_id
        else:
            tcu = TCustomerUser(user_account=user_account, group_id=group_id)
            db.session.add(tcu)
        db.session.commit()
        return result(message="操作成功")
    except Exception as e:
        return server_error(message="创建失败，请重试")


# 删除单个会员
@api.route('/config/customer/del/<int:id>', methods=['POST'])
def delete_customer(id):
    try:
        tcu = TCustomerUser.query.get(id)
        db.session.delete(tcu)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 删除多个会员
@api.route('/config/customer/batchdel', methods=['POST'])
def delete_customer_batch():
    id_list = request.form.get('ids', '').split(',')
    try:
        tcus = TCustomerUser.query.filter(TCustomerUser.id.in_(id_list)).all()
        [db.session.delete(tcu) for tcu in tcus]
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")
