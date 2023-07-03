layui.config({
    base: window.parent.baseUrl + '/layui/' //静态资源所在路径
}).use(['table', 'laydate', 'jquery'], function () {
    var table = layui.table;
    var laydate = layui.laydate;
    var $ = jQuery = layui.$;
    laydate.render({
        elem: '#loginTime'
        , type: 'datetime'
    });

    var tableIns = table.render({
        elem: '#lookupInfo'
        , url: window.parent.baseUrl + '/lookupgroup/list'
        , method: 'get'
        , cols: [
            [
                {title: '序号', templet: '#indexTpl', type: 'numbers'}
                , {field: 'groupCode', title: '编码'}
                , {field: 'groupName', title: '名称'}
                , {field: 'state', title: '状态', templet: '#switchState', unresize: true}
                , {field: 'parentGroupCode', title: '父ID'}
                , {fixed: 'right', title: '操作', align: 'center', toolbar: '#toolbar'}
            ]
        ]
        , page: true //是否显示分页
        , limit: 10
        , limits: [5, 10, 100]
        //添加权限控制
        , done: function () {
            //查看是否有查询的权限进行按钮控制
            // if(!checkShiro('add')){
            //     $("#addbtn").hide();
            // }
            // if(!checkShiro('select')){
            //     $("#selectbtn").hide();
            // }
            // if(!checkShiro('delete')){
            //     $(".del").hide();
            // }
            // if(!checkShiro('update')){
            //     $(".edit").hide();
            // }
        }
    });

    active = {
        reload: function () {
            // 执行重载
            table.reload('lookupInfo', {
                page: {
                    curr: 1
                }
            });
        }
    };

    //监听工具条
    table.on('tool(lookupInfo)', function (obj) {
        var data = obj.data;
        if (obj.event === 'edit') {
            layer.open({
                type: 2,
                title: false,
                content: '/static/view/lookup/addLookup.html?id=' + data.id,
                area: ['70%', '90%']
            });
        } else if (obj.event === 'delete') {
            layer.confirm('确认删除？', function (index) {
                $.ajax({
                    type: 'post',
                    url: window.parent.baseUrl + '/lookupgroup/deleteById/' + data.id,
                    data: {},
                    success: function (data) {
                        if (data >= 1) {
                            layer.msg('删除成功', {time: 1000});
                        } else {
                            layer.msg('删除失败', {time: 1000});
                        }
                        active.reload();
                    }
                });
                layer.close(index);
            });
        } else {
            window.open('/config/view/lookup/insideLookupItem.html?groupCode=' + data.groupCode + '&parentGroupCode=' + data.parentGroupCode, 'myFrame');
        }
    });

    $('#addLookup').on('click', function () {
        layer.open({
            type: 2,
            title: false,
            content: '/static/view/lookup/addLookup.html',
            area: ['70%', '90%']
        });
    });
});