#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class BaseModel(object):
    create_time = db.Column(db.DateTime, default=datetime.now())


# system
# 日志管理
class SysLog(BaseModel, db.Model):
    __tablename__ = "sys_log"
    id = db.Column(db.Integer, primary_key=True)
    log_ip = db.Column(db.String(50))  # IP
    business = db.Column(db.String(50))  # 日志内容
    log_user = db.Column(db.String(50))  # 操作人
    model = db.Column(db.String(50))   # 模块
    log_params = db.Column(db.String(50))  # 参数

    def to_full_dict(self):
        sl_dict = {
            "id": self.id,
            "logIp": self.log_ip,
            "business": self.business,
            "logUser": self.log_user,
            "model": self.model,
            "logParams": self.log_params,
            "createTime": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return sl_dict


# 菜单管理
class SysPermission(BaseModel, db.Model):

    __tablename__ = "sys_permission"

    id = db.Column(db.Integer, primary_key=True)
    # 权限路径
    url = db.Column(db.String(100))  # 菜单地址
    # 描述
    description = db.Column(db.String(100))  # 菜单名称
    # permission_id
    pid = db.Column(db.Integer)
    # 菜单图标
    icon = db.Column(db.String(255))  # 菜单图标
    # 菜单排序
    model_order = db.Column(db.Integer)  # 菜单排序
    # 菜单分级(1:1级菜单;2:2级菜单;3:3级菜单)
    model_level = db.Column(db.Integer)
    # 父级菜单id
    parent_id = db.Column(db.Integer)
    # 有子菜单(1:有;0:无)
    has_child = db.Column(db.Integer)
    # 路径类型（1:菜单;2:button;3:路径）
    permission_type = db.Column(db.Integer)
    # 创建人
    create_user = db.Column(db.String(100))
    # 更新时间
    update_time = db.Column(db.DateTime)
    # 更新人
    update_user = db.Column(db.String(100))

    def to_full_dict(self):
        sp_dict = {
            "id": self.id,
            "url": self.url,
            "description": self.description,
            "pid": self.pid,
            "icon": self.icon,
            "modelOrder": self.model_order,
            "modelLevel": self.model_level,
            "parentId": self.parent_id,
            "hasChild": self.has_child,
            "permissionType": self.permission_type,
            "createUser": self.create_user,
            "updateTime": self.update_time,
            "updateUser": self.update_user,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return sp_dict


# 角色管理
class SysRole(db.Model):
    __tablename__ = "sys_role"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20))  # 角色名称
    role_desc = db.Column(db.String(20))  # 角色描述

    def to_full_dict(self):
        sr_dict = {
            "id": self.id,
            "roleName": self.role_name,
            "roleDesc": self.role_desc
        }
        return sr_dict


# 外键表
class SysRolePermission(db.Model):
    __tablename__ = "sys_role_permission"
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, nullable=False)
    pers_id = db.Column(db.Integer)


# 用户管理
class SysUser(BaseModel, db.Model):
    __tablename__ = "sys_user"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=True, nullable=False)  # 用户名
    nick_name = db.Column(db.String(100))  # 昵称
    password = db.Column(db.String(100))  # 密码
    last_login_time = db.Column(db.DateTime)  # 上次登陆时间
    login_ip = db.Column(db.String(255))  # 登陆IP
    level = db.Column(db.Integer)
    state = db.Column(db.Integer)
    update_time = db.Column(db.DateTime)

    def to_full_dict(self):
        su_dict = {
            "id": self.id,
            "userName": self.user_name,
            "nickName": self.nick_name,
            "password": self.password,
            "lastLoginTime": self.last_login_time,
            "loginIp": self.login_ip,
            "level": self.level,
            "state": self.state,
            "updateTime": self.update_time,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return su_dict


# 外键表
class SysUserRole(db.Model):
    __tablename__ = "sys_user_role"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    role_id = db.Column(db.Integer)


# 系统白名单
class WhiteBlackList(BaseModel, db.Model):
    __tablename__ = "white_black_list"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(255))  # IP地址
    user_name = db.Column(db.String(255))  # 会员名称
    role_type = db.Column(db.Integer)
    remarks = db.Column(db.String(255))  # 备注
    create_user = db.Column(db.String(255))
    update_time = db.Column(db.DateTime)
    update_user = db.Column(db.String(255))

    def to_full_dict(self):
        wbl_dict = {
            "id": self.id,
            "ip": self.ip,
            "userName": self.user_name,
            "roleType": self.role_type,
            "remarks": self.remarks,
            "createUser": self.create_user,
            "updateUser": self.update_user,
            # "udpateTime": self.udpate_time,
            "createTime": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return wbl_dict


# LOOKUP管理
class TLookupGroup(BaseModel, db.Model):
    __tablename__ = "t_lookup_group"
    id = db.Column(db.Integer, primary_key=True)
    group_code = db.Column(db.String(20), unique=True)  # 编码
    group_name = db.Column(db.String(50), unique=True)  # 名称
    state = db.Column(db.Integer)  # 状态
    parent_group_code = db.Column(db.String(50))  # 父ID
    create_user = db.Column(db.String(20))
    update_user = db.Column(db.String(20))
    udpate_time = db.Column(db.DateTime)

    def to_full_dict(self):
        tlg_dict = {
            "id": self.id,
            "groupCode": self.group_code,
            "groupName": self.group_name,
            "state": self.state,
            "parentGroupCode": self.parent_group_code,
            "createUser": self.create_user,
            "updateUser": self.update_user,
            "udpateTime": self.udpate_time,
        }
        return tlg_dict


# 数据字典
class TDictionary(db.Model):
    __tablename__ = "t_dictionary"
    id = db.Column(db.Integer, primary_key=True)
    dic_key = db.Column(db.String(255))  # 字典key
    dic_value = db.Column(db.String(255))  # 字典值
    description = db.Column(db.String(255))  # 字典描述

    def to_full_dict(self):
        td_dict ={
            "id": self.id,
            "dicKey": self.dic_key,
            "dicValue": self.dic_value,
            "description": self.description
        }
        return td_dict


# pay
# 支付平台
class TPayApi(BaseModel, db.Model):
    __tablename__ = "t_pay_api"
    id = db.Column(db.Integer, primary_key=True)
    payment_code = db.Column(db.String(20), unique=True, nullable=False)  # 平台编码
    payment_name = db.Column(db.String(50))  # 平台名称
    state = db.Column(db.Integer)  # 状态
    memberid = db.Column(db.String(50))  # 商户ID
    api_key = db.Column(db.String(2000))  # apikey
    http_url = db.Column(db.String(100))  # 请求地址
    http_type = db.Column(db.String(10))  # 请求方式
    notify_url = db.Column(db.String(100))
    notify_type = db.Column(db.String(16))  # 回调类型
    callback_url = db.Column(db.String(100))
    query_url = db.Column(db.String(100))
    sign_type = db.Column(db.String(50))
    sign_format = db.Column(db.String(2000))
    param_format = db.Column(db.String(2000))
    verify_format = db.Column(db.String(2000))
    remark = db.Column(db.String(200))  # 备注
    attribute_1 = db.Column(db.String(400))
    attribute_2 = db.Column(db.String(400))
    attribute_3 = db.Column(db.String(1000))
    attribute_4 = db.Column(db.String(2000))
    attribute_5 = db.Column(db.String(2000))
    create_user = db.Column(db.String(20))
    update_user = db.Column(db.String(20))
    udpate_time = db.Column(db.DateTime)

    def to_full_dict(self):
        tpi_dict = {
            "id": self.id,
            "paymentCode": self.payment_code,
            "paymentName": self.payment_name,
            "state": self.state,
            "memberid": self.memberid,
            "apiKey": self.api_key,
            "httpUrl": self.http_url,
            "httpType": self.http_type,
            "notifyUrl": self.notify_url,
            "notifyType": self.notify_type,
            "callbackUrl": self.callback_url,
            "queryUrl": self.query_url,
            "signType": self.sign_type,
            "signFormat": self.sign_format,
            "paramFormat": self.param_format,
            "verifyFormat": self.verify_format,
            "remark": self.remark,
            "attribute1": self.attribute_1,
            "attribute2": self.attribute_2,
            "attribute3": self.attribute_3,
            "attribute4": self.attribute_4,
            "attribute5": self.attribute_5,
            "createUser": self.create_user,
            "updateUser": self.update_user,
            "udpateTime": self.udpate_time,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return tpi_dict


# 支付二维码
class TPayCode(db.Model):
    __tablename__ = "t_pay_code"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text)  # 付款二维码
    comment = db.Column(db.String(50))  # 备注
    pay_code = db.Column(db.String(50))  # 支付类型
    status = db.Column(db.Integer)  # 状态

    def to_full_dict(self):
        tpc_dict = {
            "id": self.id,
            "code": self.code,
            "comment": self.comment,
            "payCode": self.pay_code,
            "status": self.status
        }
        return tpc_dict


# 支付通道
class TPayInfo(BaseModel, db.Model):
    __tablename__ = "t_pay_info"
    id = db.Column(db.Integer, primary_key=True)
    payment_code = db.Column(db.String(20))
    payment_name = db.Column(db.String(50))  # 平台名称
    pay_code = db.Column(db.String(225))  # 支付编码
    item_name = db.Column(db.String(50))  # 支付类型名称
    item_code = db.Column(db.String(50))
    pay_model = db.Column(db.Integer)  # 支付设备
    icon = db.Column(db.String(255))  # 图标名称
    rate = db.Column(db.DECIMAL(precision=11, scale=2))  # 比例/费用
    rate_type = db.Column(db.Integer)  # 佣金类型
    state = db.Column(db.Integer)  # 状态
    min_switch = db.Column(db.String(4))  # 最小金额开关
    min_amount = db.Column(db.DECIMAL(precision=11, scale=2))  # 最小金额
    max_amount = db.Column(db.DECIMAL(precision=11, scale=2))  # 最大金额
    max_switch = db.Column(db.String(4))  # 最大金额开关
    point_switch = db.Column(db.String(4))  # 小数开关
    bank_code = db.Column(db.String(32))
    create_user = db.Column(db.String(20))
    update_user = db.Column(db.String(20))
    udpate_time = db.Column(db.DateTime)

    def to_full_dict(self):
        tpi_dict = {
            "id": self.id,
            "paymentCode": self.payment_code,
            "paymentName": self.payment_name,
            "payCode": self.pay_code,
            "itemName": self.item_name,
            "itemCode": self.item_code,
            "payModel": self.pay_model,
            "icon": self.icon,
            "rate": self.rate,
            "rateType": self.rate_type,
            "state": self.state,
            "minSwitch": self.min_switch,
            "minAmount": self.min_amount,
            "maxAmount": self.max_amount,
            "maxSwitch": self.max_switch,
            "pointSwitch": self.point_switch,
            "bankCode": self.bank_code,
            "createUser": self.create_user,
            "updateUser": self.update_user,
            "udpateTime": self.udpate_time,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return tpi_dict


# 支付类型
class TLookupItem(BaseModel, db.Model):
    __tablename__ = "t_lookup_item"
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(20))  # 类型编码
    item_name = db.Column(db.String(50))  # 类型名称
    sort = db.Column(db.Integer)  # 排序
    state = db.Column(db.Integer)  # 状态
    group_code = db.Column(db.String(20))
    parent_item_code = db.Column(db.String(20))
    attribute_1 = db.Column(db.String(100))
    attribute_2 = db.Column(db.String(100))  # 最小金额
    attribute_3 = db.Column(db.String(100))  # 最大金额
    attribute_4 = db.Column(db.String(100))  # 图标
    attribute_5 = db.Column(db.String(100))
    create_user = db.Column(db.String(20))
    update_user = db.Column(db.String(20))
    udpate_time = db.Column(db.DateTime)

    def to_full_dict(self):
        tli_dict = {
            "id": self.id,
            "itemName": self.item_name,
            "itemCode": self.item_code,
            "sort": self.sort,
            "state": self.state,
            "groupCode": self.group_code,
            "parentItemCode": self.parent_item_code,
            "attribute1": self.attribute_1,
            "attribute2": self.attribute_2,
            "attribute3": self.attribute_3,
            "attribute4": self.attribute_4,
            "attribute5": self.attribute_5,
            "createUser": self.create_user,
            "updateUser": self.update_user,
            "udpateTime": self.udpate_time,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return tli_dict


# cfg
# 会员列表
class TCustomerUser(BaseModel, db.Model):
    __tablename__ = "t_customer_user"
    id = db.Column(db.Integer, primary_key=True)
    user_account = db.Column(db.String(20), unique=True, nullable=False)  # 会员账号
    level = db.Column(db.Integer)
    amounts = db.Column(db.DECIMAL(precision=13, scale=2))
    group_id = db.Column(db.Integer)  # 级别编号
    remark = db.Column(db.String(255))
    update_time = db.Column(db.DateTime)

    def to_full_dict(self):
        tg_dict = {
            "id": self.id,
            "userAccount": self.user_account,
            "level": self.level,
            "amounts": self.amounts,
            "groupId": self.group_id,
            "remark": self.remark,
            "updateTime": self.update_time,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return tg_dict


# 会员分级
class TGroup(BaseModel, db.Model):
    __tablename__ = "t_group"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  # 分级名称
    state = db.Column(db.Integer)
    str_values = db.Column(db.String(1000))  # 支持的付款方式
    remark = db.Column(db.String(100))
    create_user = db.Column(db.String(20))
    update_user = db.Column(db.String(20))
    update_time = db.Column(db.DateTime)

    def to_full_dict(self):
        tg_dict = {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "strValues": self.str_values,
            "remark": self.remark,
            "createUser": self.create_user,
            "updateUser": self.update_user,
            "updateTime": self.update_time,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return tg_dict


# bbin订单类
class TGamePlatFormOrder(BaseModel, db.Model):
    __tablename__ = "t_game_platform_order"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(255))
    order_id = db.Column(db.String(255))
    amount = db.Column(db.DECIMAL(precision=12, scale=2))
    created_at = db.Column(db.String(255))
    username = db.Column(db.String(255))
    notify_url = db.Column(db.String(255))
    method_id = db.Column(db.String(255))
    bank_id = db.Column(db.String(255))
    sign = db.Column(db.String(255))
    status = db.Column(db.Integer)
    notify_time = db.Column(db.DateTime)


# order
# 订单
class TOrder(BaseModel, db.Model):
    __tablename__ = "t_order"
    id = db.Column(db.Integer, primary_key=True)
    user_account = db.Column(db.String(20))  # 用户名
    order_id = db.Column(db.String(255), unique=True, nullable=False)  # 订单编码
    order_amount = db.Column(db.DECIMAL(precision=10, scale=2))  # 订单金额
    #  支付状态 INIT(0, "全部状态"), PAYING(10, "支付处理中"),PAY_FILED(20, "支付失败"), PAY_SUCCESS(30,"支付成功");
    order_state = db.Column(db.Integer)  # 订单状态
    order_desc = db.Column(db.String(255))
    order_time = db.Column(db.DateTime)
    user_ip = db.Column(db.String(50))
    payment_code = db.Column(db.String(255))  # 订单来源
    pay_code = db.Column(db.String(100))
    pay_order = db.Column(db.String(255))
    item_code = db.Column(db.String(255))  # 支付方式
    #  ALL(0, "全部状态"), OPE_TO_DO(10, "待处理"), OPE_LOCKED(20, "已锁定"), OPE_TO_CONFIRM(30, "待确认"),
    #  OPE_CONFIRM(40, "已确定" ),OPE_CANCEL(50, "已取消")
    state = db.Column(db.Integer)
    rate = db.Column(db.DECIMAL(precision=10, scale=2))
    # 手续费
    rate_amount = db.Column(db.DECIMAL(precision=10, scale=2))
    lock_id = db.Column(db.String(20))
    external_id = db.Column(db.Integer)
    update_time = db.Column(db.DateTime)
    update_user = db.Column(db.String(30))

    def to_full_dict(self):
        to_dict = {
            "id": self.id,
            "userAccount": self.user_account,
            "orderId": self.order_id,
            "orderAmount": self.order_amount,
            "orderState": self.order_state,
            "orderDesc": self.order_desc,
            "orderTime": self.order_time,
            "userIp": self.user_ip,
            "paymentCode": self.payment_code,
            "payCode": self.pay_code,
            "payOrder": self.pay_order,
            "itemCode": self.item_code,
            "state": self.state,
            "rate": self.rate,
            "rateAmount": self.rate_amount,
            "lockId": self.lock_id,
            "externalId": self.external_id,
            "updateTime": self.update_time,
            "updateUser": self.update_user,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return to_dict


# 每日订单统计
# class TOrderDaliySum(BaseModel, db.Model):
#     __tablename__ = "t_order_daliy_sum"
#     order_date = DateField(primary_key=True)
#     number = IntegerField(null=True)
#     amount = DecimalField(max_digits=10, decimal_places=2, null=True)
#     amount_rate = DecimalField(max_digits=10, decimal_places=2, null=True)
#     order_state = DecimalField(max_digits=10, decimal_places=2, null=True)
#     amount_success = DecimalField(max_digits=20, decimal_places=2, null=True)
#     amount_fail = DecimalField(max_digits=20, decimal_places=2, null=True)
#     number_success = IntegerField(null=True)
#     number_fail = IntegerField(null=True)
#     on_pay_order_id = CharField(max_length=255, null=True)


# 历史订单列表
class TOrderHis(BaseModel, db.Model):
    __tablename__ = "t_order_his"
    id = db.Column(db.Integer, primary_key=True)
    user_account = db.Column(db.String(20))  # 用户名
    order_id = db.Column(db.String(255), unique=True, nullable=False)  # 订单编码
    order_amount = db.Column(db.DECIMAL(precision=10, scale=2))  # 订单金额
    order_state = db.Column(db.Integer)  # 订单状态
    order_desc = db.Column(db.String(255))
    order_time = db.Column(db.DateTime)
    user_ip = db.Column(db.String(50))
    payment_code = db.Column(db.String(255))  # 订单来源
    pay_code = db.Column(db.String(100))
    pay_order = db.Column(db.String(255))
    item_code = db.Column(db.String(255))  # 支付方式
    state = db.Column(db.Integer)
    rate = db.Column(db.DECIMAL(precision=10, scale=2))
    # 手续费
    rate_amount = db.Column(db.DECIMAL(precision=10, scale=2))
    lock_id = db.Column(db.String(20))
    update_time = db.Column(db.DateTime)
    update_user = db.Column(db.String(30))
    batch_no = db.Column(db.Integer)

    def to_full_dict(self):
        toh_dict = {
            "id": self.id,
            "userAccount": self.user_account,
            "orderId": self.order_id,
            "orderAmount": self.order_amount,
            "orderState": self.order_state,
            "orderDesc": self.order_desc,
            "orderTime": self.order_time,
            "userIp": self.user_ip,
            "paymentCode": self.payment_code,
            "payCode": self.pay_code,
            "payOrder": self.pay_order,
            "itemCode": self.item_code,
            "state": self.state,
            "rate": self.rate,
            "rateAmount": self.rate_amount,
            "lockId": self.lock_id,
            "updateTime": self.update_time,
            "updateUser": self.update_user,
            "batchNo": self.batch_no,
            "createTimeStr": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return toh_dict
