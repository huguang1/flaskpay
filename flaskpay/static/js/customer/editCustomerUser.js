layui.use(['form', 'layedit', 'laydate'], function () {
    var form = layui.form
        , layer = layui.layer
        , layedit = layui.layedit
        , laydate = layui.laydate;
    //监听提交
    form.on('submit(save)', function (data) {
        $.ajax({
            type: "post",
            url: "/config/customer/save",
            data: data.field,
            success: function (data) {
                layer.msg(data.message);
                if (data.code == 200) {
                    setTimeout(function () {
                        var index = parent.layer.getFrameIndex(window.name); //先得到当前iframe层的索引
                        parent.layer.close(index); //再执行关闭
                    }, 1000);
                }
            }
        });
        return false;
    });

    function renderForm() {
        layui.use('form', function () {
            var form = layui.form;
            form.render();
        });
    }

    $(function () {
        $.ajax({
            type: "GET",
            url: "/config/group/box",
            data: {},
            async: false,//这里设置为同步，异步表格渲染不加载
            dataType: "json",
            success: function (data) {
                data = data.data;
                for (var i = 0 in data) {
                    $("#groupId").append("<option value=" + data[i].id + ">" + data[i].name + "</option>");
                    renderForm();
                }
            }
        });
    })

});

function inputMemberInfo(data) {
    $('input[name="userAccount"]').val(data.userAccount);
    $("#groupId").val(data.groupId);
    $("#id").val(data.id);
    layui.form.render('select');
}