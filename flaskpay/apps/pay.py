#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
# 支持二维码的支付通道
from . import api
from flaskpay.models import TPayInfo, TPayCode, TLookupItem, TPayApi
from flaskpay.utils.restful import data_return, server_error, result, params_error
from flask import request
import base64
from flaskpay import db


# 获取有二维码的支付通道
@api.route('/config/payCode/getList')
def get_paycode_info_list():
    try:
        values = TPayInfo.query.filter(TPayInfo.payment_code == 'erweima').all()
        return data_return(data=[value.to_full_dict() for value in values])
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 二维码展示
@api.route('/config/payCode/payCodeView')
def get_paycode_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    pay_code = request.args.get('payCode', '')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = TPayCode.query.filter(TPayCode.pay_code.contains(pay_code)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 增加二维码
@api.route('/config/payCode/filesUpload', methods=['POST'])
def create_paycode():
    payType = request.form.get('payType', None)
    comment = request.form.get('comment', None)
    files = request.files
    comment = files['file'].filename
    body = files['file'].read()
    body = "data:image/png;base64," + str(base64.b64encode(body), encoding='utf-8')
    try:
        td = TPayCode(code=body, comment=comment, pay_code=payType, status=1)
        db.session.add(td)
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 删除二维码
@api.route('/config/payCode/deleteCode/<int:id>', methods=['POST'])
def delete_paycode(id):
    try:
        td = TPayCode.query.get(id)
        db.session.delete(td)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 更改二维码
@api.route('/config/payCode/updateCodeState/<int:id>', methods=['POST'])
def update_paycode(id):
    status = request.form.get('status', None)
    try:
        td = TPayCode.query.get(id)
        td.status = status
        db.session.commit()
        return result(message="更改成功")
    except Exception as e:
        return server_error(message="更改失败，请重试！")


# 支付类型展示
@api.route('/config/lookupitem/getLookupItemByGroupCodePage')
def get_lookup_groupcode():
    groupCode = request.args.get('groupCode', '')
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    state = request.args.get('state', None)
    try:
        page_int = int(page)
        limit_int = int(limit)
        if state:
            values = TLookupItem.query.filter(TLookupItem.group_code == groupCode, TLookupItem.state == state).paginate(page_int, limit_int)
        else:
            values = TLookupItem.query.filter(TLookupItem.group_code == groupCode).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 添加支付类型
@api.route('/config/lookupitem/save', methods=['POST'])
def create_lookupitem():
    attribute_1 = request.form.get('attribute1', None)
    attribute_2 = request.form.get('attribute2', None)
    attribute_3 = request.form.get('attribute3', None)
    attribute_4 = request.form.get('attribute4', None)
    attribute_5 = request.form.get('attribute5', None)
    group_code = request.form.get('groupCode', None)
    id = request.form.get('id', '')
    item_code = request.form.get('itemCode', None)
    item_name = request.form.get('itemName', None)
    sort = request.form.get('sort', None)
    state = request.form.get('state', None)
    try:
        if id == '':
            tli = TLookupItem(attribute_1=attribute_1, attribute_2=attribute_2, attribute_3=attribute_3, attribute_4=attribute_4, attribute_5=attribute_5, group_code=group_code, item_code=item_code, item_name=item_name, sort=sort, state=state)
            db.session.add(tli)
            db.session.commit()
            return result(message="添加成功")
        else:
            tli = TLookupItem.query.get(id)
            tli.attribute_1 = attribute_1
            tli.attribute_2 = attribute_2
            tli.attribute_3 = attribute_3
            tli.attribute_4 = attribute_4
            tli.attribute_5 = attribute_5
            tli.group_code = group_code
            tli.item_code = item_code
            tli.item_name = item_name
            tli.sort = sort
            tli.state = state
            db.session.commit()
            return result(message="更改成功")
    except Exception as e:
        return params_error(message="添加失败，请重试")


# 删除支付类型
@api.route('/config/lookupitem/deleteById/<int:id>', methods=['POST'])
def delete_lookupitem(id):
    try:
        tli = TLookupItem.query.get(id)
        db.session.delete(tli)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 获取单个支付类型
@api.route('/config/lookupitem/info/<int:id>')
def get_lookupitem_info(id):
    try:
        tli = TLookupItem.query.get(id)
        return data_return(data=tli.to_full_dict())
    except Exception as e:
        return server_error(message="获取失败，请重试")


# 获取支付平台
@api.route('/config/payapi/list')
def get_payapi_list():
    page = request.args.get('page', None)
    limit = request.args.get('limit', None)
    paymentCode = request.args.get('paymentCode', '')
    try:
        if page is not None and limit is not None:
            if page == '' or limit == '':
                page_int = 1
                limit_int = 10
            page_int = int(page)
            limit_int = int(limit)
            values = TPayApi.query.filter(TPayApi.payment_code.contains(paymentCode) | TPayApi.payment_name.contains(paymentCode)).paginate(page_int, limit_int)
            items = values.items
            count = values.total
        else:
            items = TPayApi.query.all()
            count = len(items)
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 添加支付平台
@api.route('/config/payapi/save', methods=['POST'])
def create_payapi():
    api_key = request.form.get('apiKey', None)
    attribute_1 = request.form.get('attribute1', None)
    attribute_2 = request.form.get('attribute2', None)
    attribute_3 = request.form.get('attribute3', None)
    attribute_4 = request.form.get('attribute4', None)
    attribute_5 = request.form.get('attribute5', None)
    callback_url = request.form.get('callbackUrl', None)
    http_type = request.form.get('httpType', None)
    http_url = request.form.get('httpUrl', None)
    id = request.form.get('id', '')
    memberid = request.form.get('memberid', None)
    notify_type = request.form.get('notifyType', None)
    notify_url = request.form.get('notifyUrl', None)
    param_format = request.form.get('paramFormat', None)
    payment_code = request.form.get('paymentCode', None)
    payment_name = request.form.get('paymentName', None)
    query_url = request.form.get('queryUrl', None)
    remark = request.form.get('remark', None)
    sign_format = request.form.get('signFormat', None)
    sign_type = request.form.get('signType', None)
    state = request.form.get('state', None)
    verify_format = request.form.get('verifyFormat', None)
    try:
        if id == '':
            tpi = TPayApi(api_key=api_key, attribute_1=attribute_1, attribute_2=attribute_2, attribute_3=attribute_3,
                          attribute_4=attribute_4,attribute_5=attribute_5, callback_url=callback_url, http_type=http_type,
                          http_url=http_url, memberid=memberid,notify_type=notify_type, notify_url=notify_url,
                          param_format=param_format, payment_code=payment_code, payment_name=payment_name,query_url=query_url,
                          remark=remark, sign_format=sign_format, sign_type=sign_type, state=state, verify_format=verify_format)
            db.session.add(tpi)
            db.session.commit()
            return result(message="添加成功")
        else:
            tli = TPayApi.query.get(id)
            tli.api_key = api_key
            tli.attribute_1 = attribute_1
            tli.attribute_2 = attribute_2
            tli.attribute_3 = attribute_3
            tli.attribute_4 = attribute_4
            tli.attribute_5 = attribute_5
            tli.callback_url = callback_url
            tli.http_type = http_type
            tli.http_url = http_url
            tli.memberid = memberid
            tli.notify_type = notify_type
            tli.notify_url = notify_url
            tli.param_format = param_format
            tli.payment_code = payment_code
            tli.payment_name = payment_name
            tli.query_url = query_url
            tli.remark = remark
            tli.sign_format = sign_format
            tli.sign_type = sign_type
            tli.state = state
            tli.verify_format = verify_format
            db.session.commit()
            return result(message="更改成功")
    except Exception as e:
        return params_error(message="添加失败，请重试")


# 删除支付平台
@api.route('/config/payapi/deleteById/<int:id>', methods=['POST'])
def delete_payapi(id):
    try:
        tli = TPayApi.query.get(id)
        db.session.delete(tli)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 获取单个支付平台
@api.route('/config/payapi/info/<int:id>')
def get_payapi_info(id):
    try:
        tli = TPayApi.query.get(id)
        return data_return(data=tli.to_full_dict())
    except Exception as e:
        return server_error(message="获取失败，请重试")


# 获取不分页的支付类型
@api.route('/config/lookupitem/getLookupItemByGroupCode')
def get_lookupitem_groupcode_all():
    groupCode = request.args.get('groupCode', '')
    state = request.args.get('state', None)
    try:
        if state:
            values = TLookupItem.query.filter(TLookupItem.group_code == groupCode, TLookupItem.state == state).all()
        else:
            values = TLookupItem.query.filter(TLookupItem.group_code == groupCode).all()
        count = len(values)
        return data_return(data=[value.to_full_dict() for value in values], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 支付通道展示
@api.route('/config/payinfo/all')
def get_payinfo():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    payment_code = request.args.get('paymentCode', '')
    item_code = request.args.get('itemCode', '')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = TPayInfo.query.filter(TPayInfo.payment_code.contains(payment_code), TPayInfo.item_code.contains(item_code)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 添加支付通道
@api.route('/config/payinfo/save', methods=['POST'])
def create_payinfo():
    bank_code = request.form.get('bankCode', None)
    id = request.form.get('id', '')
    item_code = request.form.get('itemCode', '')
    max_amount = request.form.get('maxAmount', None)
    max_switch = request.form.get('maxSwitch', None)
    min_amount = request.form.get('minAmount', None)
    min_switch = request.form.get('minSwitch', None)
    pay_code = request.form.get('payCode', None)
    payment_code = request.form.get('paymentCode', '')
    point_switch = request.form.get('pointSwitch', None)
    rate = request.form.get('rate', None)
    rate_type = request.form.get('rateType', None)
    state = request.form.get('state', None)
    wangyinType = request.form.get('wangyinType', None)
    try:
        lookup = TLookupItem.query.filter(TLookupItem.item_code==item_code).first()
        if lookup.attribute_1 == 'PC':
            pay_model = 1
        elif lookup.attribute_1 == 'WAP':
            pay_model = 2
        elif lookup.attribute_1 == '网银内部':
            pay_model = 3
        elif lookup.attribute_1 == '网银外部':
            pay_model = 4
        else:
            pay_model = 0
        item_name = lookup.item_name
        icon = lookup.attribute_4
        payapi = TPayApi.query.filter(TPayApi.payment_code==payment_code).first()
        payment_name = payapi.payment_name
        if id == '':
            tpi = TPayInfo(bank_code=bank_code, item_code=item_code, max_amount=max_amount, max_switch=max_switch,
                           min_amount=min_amount,min_switch=min_switch, pay_code=pay_code, payment_code=payment_code,
                           point_switch=point_switch, rate=rate,rate_type=rate_type, state=state, pay_model=pay_model,
                           item_name=item_name, icon=icon, payment_name=payment_name)
            db.session.add(tpi)
            db.session.commit()
            return result(message="添加成功")
        else:
            tli = TPayInfo.query.get(id)
            tli.bank_code = bank_code
            tli.item_code = item_code
            tli.max_amount = max_amount
            tli.max_switch = max_switch
            tli.min_amount = min_amount
            tli.min_switch = min_switch
            tli.pay_code = pay_code
            tli.payment_code = payment_code
            tli.point_switch = point_switch
            tli.rate = rate
            tli.rate_type = rate_type
            tli.state = state
            tli.pay_model = pay_model
            tli.icon = icon
            tli.payment_name = payment_name
            db.session.commit()
            return result(message='修改成功')
    except Exception as e:
        return params_error(message="添加失败，请重试")


# 删除支付通道
@api.route('/config/payinfo/deleteById/<int:id>', methods=['POST'])
def delete_payinfo(id):
    try:
        tli = TPayInfo.query.get(id)
        db.session.delete(tli)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 获取单个支付通道
@api.route('/config/payinfo/info/<int:id>')
def get_payinfo_info(id):
    try:
        tli = TPayInfo.query.get(id)
        return data_return(data=tli.to_full_dict())
    except Exception as e:
        return server_error(message="获取失败，请重试")
