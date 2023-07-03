#!/usr/bin/pyhton
# -*- coding: utf-8 -*-
# @Author: xiaoli
# @Time: 2019/6/19
import random
import datetime
import jwt
from flask import request, session, g, current_app, sessions, make_response
from config import Config
from . import api
from PIL import Image, ImageDraw, ImageFont
import io
import hashlib
from flaskpay.models import SysUser, SysUserRole, SysPermission, TDictionary, TLookupGroup, WhiteBlackList, SysLog, \
    SysRole, SysRolePermission
from flaskpay.utils.restful import params_error, ok, data_return, server_error, result
from flaskpay import db, redis_store
from flaskpay.utils.common import login_required
from flaskpay.utils.create_token import get_token


# 获取验证登陆页面的token值
@api.route('/config/getlogin/token', methods=['POST'])
def get_login_token():
    num = random.randint(100000000, 999999999)
    payload = {'function': 'login', 'num': num, 'time': datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")}
    token = str(jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256'), encoding="utf-8")
    response = make_response(result(message='获取验证登陆页面的token值正确'))
    response.set_cookie('loginToken', token, 60*5)  # 这个是jwt加密后的token值，所以明文存储没有问题，存储时间设置为五分钟
    return response


# 验证码
@api.route('/config/cache')
def get_cache():
    """
    这个验证码的功能是，后台生成随机数，保存在django的session中，同时将这个随机数做成图片，并增加一些噪点，
    传递给前端并展示出来。
    """
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = '#3D1769'
    width = 100
    height = 40
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象，ubuntu的字体路径为“/usr/share/fonts/truetype/freefont”
    font = ImageFont.truetype('FreeMono.ttf', 33)  # linux
    # font = ImageFont.truetype('arial.ttf', 33)  # win7的
    # 构造字体颜色
    # 选取验证码的背景颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    # 存入redis，用于做进一步验证
    # self.redis_conn.set(Constants["REDIS_CONFIG_CACHE_CODE"], rand_str)
    # 内存文件操作
    buf = io.BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    response = make_response(buf.getvalue())
    response.headers['Content-type'] = 'image/png'
    response.set_cookie('verification_code', rand_str, 60*10)  # 验证码存储时间为10分钟
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return response


# 登陆校验并返回token值
@api.route('/check/login', methods=['POST'])
def set_login():
    cookieToken = request.cookies.get('loginToken')
    headerToken = request.headers["X-CSRF-TOKEN"]
    if cookieToken != headerToken:
        return params_error(message="CSRF校验不能通过，请重试！")
    username = request.form.get('username', '')
    password = request.form.get('password', None)
    hl = hashlib.md5()
    if not password:
        return params_error(message="密码不正确，请重试！")
    hl.update(password.encode(encoding='utf-8'))
    password = hl.hexdigest()
    try:
        value = SysUser.query.filter(SysUser.user_name==username, SysUser.password==password).first()
        role = SysUserRole.query.filter(SysUserRole.user_id==value.id)
        if not role:
            return params_error(message="用户没有角色，请重试！")
        token = get_token(role, username)
        response = make_response(ok())
        # 带有用户信息的token，存储时间为30分钟
        response.set_cookie('token', token, 60*30)
        # 将token值存储在redis中
        redis_store.set('token:%s' % username, token, ex=60*30)
        # 将用户名储存到cookie,或者叫session中
        session['username'] = username
        session.permanent = True
        return response
    except Exception as e:
        return params_error(message="用户不存在，请重试！")


# 获取到首页菜单
@api.route('/config/menu/userMenuList')
def get_menu_userlist():
    try:
        values = SysPermission.query.filter(SysPermission.model_level==1).order_by('model_order').all()
        content = []
        for value in values:
            children = []
            childs = SysPermission.query.filter(SysPermission.parent_id==value.id)
            for child in childs:
                child_dict = {
                    "level": child.model_level,
                    "icon": child.icon,
                    "description": child.description,
                    "url": child.url,
                    "order": child.model_order
                }
                children.append(child_dict)
            data = {
                "level": value.model_level,
                "icon": value.icon,
                "description": value.description,
                "url": value.url,
                "order": value.model_order,
                "children": children
            }
            content.append(data)
        return data_return(data=content)
    except Exception as e:
        return server_error(message="用户数据不存在，请重试")


# 获取登陆管理员
@api.route('/config/init/getUserName')
@login_required
def get_user_name():
    username = g.username
    if username:
        return result(message=username)
    else:
        return params_error(message="用户已过期")


# 退出页面
@api.route('/logout', methods=['POST'])
@login_required
def logout():
    username = g.username
    response = make_response(ok())
    # 清除用户的token值
    response.set_cookie('token', '')
    # 将redis中存储的token值清除
    redis_store.delete('token:%s' % username)
    # 将session中的用户清除
    session.pop('username', None)
    return response


# 数据字典所有信息展示
@api.route('/config/dictionary/list')
def get_dictionary_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    search_value = request.args.get("searchValue", '')
    search_key = request.args.get("searchKey", '')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = TDictionary.query.filter(TDictionary.dic_key.contains(search_key), TDictionary.dic_value.contains(search_value)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="字典数据不存在，请重试")


# 添加数据字典
@api.route('/config/dictionary/save', methods=['POST'])
def create_dictionary():
    dic_key = request.form.get('dicKey', None)
    dic_value = request.form.get('dicValue', None)
    description = request.form.get('description', None)
    try:
        td = TDictionary(dic_key=dic_key, dic_value=dic_value, description=description)
        db.session.add(td)
        db.session.commit()
        return result(message='添加成功')
    except Exception as e:
        return server_error(message="插入数据失败，请重试")


# 删除字典
@api.route('/config/dictionary/del/<int:id>', methods=['POST'])
def delete_dictionary(id):
    try:
        td = TDictionary.query.get(id)
        db.session.delete(td)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 修改字典
@api.route('config/dictionary/update', methods=['POST'])
def update_dictionary():
    id = request.form.get('id', None)
    dic_key = request.form.get('dicKey', None)
    dic_value = request.form.get('dicValue', None)
    description = request.form.get('description', None)
    try:
        td = TDictionary.query.get(id)
        td.dic_key = dic_key
        td.dic_value = dic_value
        td.description = description
        db.session.commit()
        return result(message='修改成功')
    except Exception as e:
        return server_error(message="修改失败，请重试")


#lookup所有信息展示
@api.route('/config/lookupgroup/list')
def get_lookup_group_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = TLookupGroup.query.filter().paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 添加lookup
@api.route('/config/lookupgroup/save', methods=['POST'])
def create_lookupgroup():
    group_code = request.form.get('groupCode', None)
    group_name = request.form.get('groupName', None)
    id = request.form.get('id', None)
    parent_group_code = request.form.get('parentGroupCode', None)
    state = request.form.get('state', None)
    if id:
        tlg = TLookupGroup.query.get(id)
        tlg.group_code = group_code
        tlg.group_name = group_name
        tlg.parent_group_code = parent_group_code
        tlg.state = state
        db.session.commit()
        return result(message='添加成功')
    else:
        try:
            tlg = TLookupGroup(group_code=group_code, group_name=group_name, state=state, parent_group_code=parent_group_code)
            db.session.add(tlg)
            db.session.commit()
            return result(message='添加成功')
        except Exception as e:
            return server_error(message="插入数据失败，请重试")


# 查询单个lookup
@api.route('/config/lookupgroup/info')
def get_lookup_group_info():
    id = request.args.get('id', None)
    try:
        tlg = TLookupGroup.query.get(id)
        return result(data=tlg.to_full_dict())
    except Exception as e:
        return server_error(message="查询lookup失败，请重试")


# 删除lookup
@api.route('/config/lookupgroup/deleteById/<int:id>', methods=['POST'])
def delete_lookup_group(id):
    try:
        td = TLookupGroup.query.get(id)
        db.session.delete(td)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 系统白名单信息展示
@api.route('/config/blackWhite/whiteList')
def get_black_whilte_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    key = request.args.get('key', '')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = WhiteBlackList.query.filter(WhiteBlackList.role_type == 0, WhiteBlackList.user_name.contains(key)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查找失败，请重试")


# 添加系统白名单
@api.route('/config/blackWhite/addWhite', methods=['POST'])
def create_white():
    user_name = request.form.get("userName", None)
    ip = request.form.get("ip", None)
    remarks = request.form.get("remarks", None)
    try:
        wbl = WhiteBlackList(ip=ip, user_name=user_name, remarks=remarks, role_type=0)
        db.session.add(wbl)
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 删除系统白名单
@api.route('/config/blackWhite/delete/<int:id>', methods=['POST'])
def delete_white(id):
    try:
        td = WhiteBlackList.query.get(id)
        db.session.delete(td)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 删除多个系统白名单
@api.route('/config/blackWhite/batchDelete', methods=['POST'])
def delete_white_batch():
    id_list = request.form.get('ids', '').split(',')
    try:
        values = WhiteBlackList.query.filter(WhiteBlackList.id.in_(id_list)).all()
        [db.session.delete(u) for u in values]
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 用户黑名单展示
@api.route('/config/blackWhite/blackList')
def get_black_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    key = request.args.get('key', '')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = WhiteBlackList.query.filter(WhiteBlackList.role_type == 1, WhiteBlackList.user_name.contains(key)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查询信息失败，请重试")


# 添加用户黑名单
@api.route('/config/blackWhite/addBlack', methods=['POST'])
def create_black():
    user_name = request.form.get("userName", None)
    ip = request.form.get("ip", None)
    remarks = request.form.get("remarks", None)
    try:
        wbl = WhiteBlackList(ip=ip, user_name=user_name, remarks=remarks, role_type=1)
        db.session.add(wbl)
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 日志管理信息展示
@api.route('/config/sys/log/list')
def get_sys_log_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    log_user = request.args.get('logUser', '')
    create_time = request.args.get('createTime', None)
    end_time = request.args.get('endTime', None)
    try:
        page_int = int(page)
        limit_int = int(limit)
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else datetime.datetime.now()
        create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S") if create_time else datetime.datetime.strptime("1971-01-01 18:55:23", "%Y-%m-%d %H:%M:%S")
        values = SysLog.query.filter(SysLog.create_time <= end_time, SysLog.create_time >= create_time, SysLog.log_user.contains(log_user)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查询信息失败，请重试")


# 批量删除日志记录
@api.route('/config/sys/log/batchDelete', methods=['POST'])
def delete_log():
    id_list = request.form.get('logIds', '').split(',')
    try:
        values = SysLog.query.filter(SysLog.id.in_(id_list)).all()
        [db.session.delete(u) for u in values]
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 清空日志记录
@api.route('/config/sys/log/clearlog', methods=['POST'])
def clear_log():
    try:
        values = SysLog.query.filter()
        [db.session.delete(u) for u in values]
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 菜单管理信息展示
@api.route('/config/sys/permission/list')
def get_sys_permission_list():
    page = request.args.get('page', None)
    limit = request.args.get('limit', None)
    key = request.args.get('key', '')
    try:
        if page is not None or limit is not None:
            if page == '' or limit == '':
                page = 1
                limit = 10
            else:
                page = int(page)
                limit = int(limit)
            values = SysPermission.query.filter(SysPermission.description.contains(key)).paginate(page, limit)
            count = values.total
            values = values.items
        else:
            values = SysPermission.query.filter(SysPermission.description.contains(key)).all()
            count = len(values)
        return data_return(data=[item.to_full_dict() for item in values], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查询信息失败，请重试")


# 添加菜单管理
@api.route('/config/sys/permission/save', methods=['POST'])
def create_permission():
    description = request.form.get("description", None)
    url = request.form.get("url", None)
    icon = request.form.get("icon", None)
    parent_id = request.form.get("parentId", None)
    model_order = request.form.get("modelOrder", None)
    try:
        sp = SysPermission(description=description, url=url, icon=icon, parent_id=parent_id, model_order=model_order)
        db.session.add(sp)
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 删除菜单管理
@api.route('/config/sys/permission/delete/<int:id>', methods=['POST'])
def delete_permission(id):
    try:
        sp = SysPermission.query.get(id)
        db.session.delete(sp)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 更新菜单管理
@api.route('/config/sys/permission/update', methods=['POST'])
def update_permission():
    id = request.form.get('id', None)
    url = request.form.get('url', None)
    parent_id = request.form.get('parentId', None)
    icon = request.form.get('icon', None)
    model_order = request.form.get('modelOrder', None)
    description = request.form.get('description', None)
    try:
        td = SysPermission.query.get(id)
        td.url = url
        td.parent_id = parent_id
        td.icon = icon
        td.model_order = model_order
        td.description = description
        db.session.commit()
        return result(message='修改成功')
    except Exception as e:
        return server_error(message="修改失败，请重试")


# 角色管理信息展示
@api.route('/config/sys/role/list')
def get_role_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    key = request.args.get('key', '')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = SysRole.query.filter(SysRole.role_name.contains(key)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        return data_return(data=[item.to_full_dict() for item in items], kwargs={"count": count})
    except Exception as e:
        return server_error(message="查询信息失败，请重试")


# 添加角色管理
@api.route('/config/sys/role/save', methods=['POST'])
def create_role():
    role_name = request.form.get('roleName', None)
    role_desc = request.form.get('roleDesc', None)
    id_list = request.form.getlist('id')
    try:
        sr = SysRole(role_name=role_name, role_desc=role_desc)
        db.session.add(sr)
        db.session.commit()
        [db.session.add(SysRolePermission(pers_id=id, role_id=sr.id)) for id in id_list]
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 删除角色管理
@api.route('/config/sys/role/delete/<int:id>', methods=['POST'])
def delete_role(id):
    try:
        sp = SysRole.query.get(id)
        srp = SysRolePermission.query.filter(SysRolePermission.role_id == id)
        [db.session.delete(u) for u in srp]
        db.session.delete(sp)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 修改角色管理之前，需要查看角色由什么权限
@api.route('/config/sys/role/queryPermisson')
def get_role_permission():
    id = request.args.get('roleId', None)
    try:
        values = SysRolePermission.query.filter(SysRolePermission.role_id == id).all()
        str = ','.join(["%s" % value.pers_id for value in values])
        return result(data=str)
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 修改角色管理
@api.route('/config/sys/role/update', methods=['POST'])
def update_role():
    id_list = request.form.getlist('id')
    role_id = request.form.get('roleId')
    role_name = request.form.get('roleName')
    role_desc = request.form.get('roleDesc')
    try:
        sr = SysRole.query.get(role_id)
        sr.role_name = role_name
        sr.role_desc = role_desc
        db.session.add(sr)
        d_srp = SysRolePermission.query.filter(SysRolePermission.role_id == role_id)
        [db.session.delete(srp) for srp in d_srp]
        [db.session.add(SysRolePermission(role_id=role_id, pers_id=id)) for id in id_list]
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 用户管理展示
@api.route('/config/sys/user/list')
def get_user_list():
    page = request.args.get('page', '1')
    limit = request.args.get('limit', '10')
    key = request.args.get('keyWord', '')
    try:
        page_int = int(page)
        limit_int = int(limit)
        values = SysUser.query.filter(SysUser.user_name.contains(key)).paginate(page_int, limit_int)
        items = values.items
        count = values.total
        data_list = []
        for item in items:
            children = []
            item_dict = item.to_full_dict()
            role_id = SysUserRole.query.filter(SysUserRole.user_id == item.id).all()
            role_id_list = [role.role_id for role in role_id]
            roles = SysRole.query.filter(SysRole.id.in_(role_id_list)).all()
            for role in roles:
                children.append(role.to_full_dict())
            item_dict["roleList"] = children
            data_list.append(item_dict)
        return data_return(data=data_list, kwargs={"count": count})
    except Exception as e:
        return server_error(message="查询信息失败，请重试")


# 添加用户管理
@api.route('/config/sys/user/save', methods=['POST'])
def create_user():
    user_name = request.form.get('userName', None)
    nick_name = request.form.get('nickName', None)
    role_id = request.form.get('roleId', '').split(',')
    password = request.form.get('password', None)
    repassword = request.form.get('repassword', None)
    if len(password) < 6 or password != repassword:
        return params_error(message='密码输入有误，请重试！')
    hl = hashlib.md5()
    hl.update(password.encode(encoding='utf-8'))
    password = hl.hexdigest()
    try:
        su = SysUser(user_name=user_name, nick_name=nick_name, password=password)
        db.session.add(su)
        db.session.commit()
        [db.session.add(SysUserRole(user_id=su.id, role_id=id)) for id in role_id]
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")


# 删除用户管理
@api.route('/config/sys/user/delete/<int:id>', methods=['POST'])
def delete_user(id):
    try:
        su = SysUser.query.get(id)
        sur = SysUserRole.query.filter(SysUserRole.user_id == id)
        [db.session.delete(u) for u in sur]
        db.session.delete(su)
        db.session.commit()
        return result(message='删除成功')
    except Exception as e:
        return server_error(message="删除失败，请重试")


# 修改用户管理
@api.route('/config/sys/user/updateUser/<int:id>', methods=['POST'])
def update_user(id):
    user_name = request.form.get('userName', None)
    nick_name = request.form.get('nickName', None)
    role_id = request.form.get('roleId', '').split(',')
    password = request.form.get('password', None)
    repassword = request.form.get('repassword', None)
    if len(password) < 6 or password != repassword:
        return params_error(message='密码输入有误，请重试！')
    hl = hashlib.md5()
    hl.update(password.encode(encoding='utf-8'))
    password = hl.hexdigest()
    try:
        su = SysUser.query.get(id)
        su.user_name = user_name
        su.nick_name = nick_name
        su.password = password
        sur = SysUserRole.query.filter(SysUserRole.user_id == id)
        [db.session.delete(u) for u in sur]
        [db.session.add(SysUserRole(user_id=su.id, role_id=id)) for id in role_id]
        db.session.commit()
        return result(message="添加成功")
    except Exception as e:
        return server_error(message="添加失败，请重试")
