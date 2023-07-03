$(function () {
    getPayType();
    renderForm();
    getDetail();
})
function getPayType() {
    //数据库里面检查
    $.ajax({
        type: "get",  //使用提交的方法 post、get
        url: "/config/lookupitem/getLookupItemByGroupCode?groupCode=PAY_TYPE&state=1",   //提交的地址
        async: false,
        dataType: "json"//返回数据类型的格式
    }).done(function (result) {//回调操作
        data = result.data;
        var html = '';
        $("#formData").html("");
        html += '<div class="layui-form-item">'
        html += '<label class="layui-form-label">分级名称</label>'
        html += '<div class="layui-input-inline">'
        html += '<input type="hidden" id="id" name="id" value="" />'
        html += '<input	type="text" id="name" name="name" value="" lay-verify="required" placeholder="分级名称" autocomplete="off" class="layui-input"/>'
        html += '</div>'
        html += '</div>'

        for (var i in data) {
            if (!isNaN(i)) {
                html += '<div class="layui-form-item">'
                html += '<div class="layui-inline">'
                html += '<label class="layui-form-label">' + data[i].itemName + '</label>'
                html += '<div class="layui-input-inline layui-form" lay-filter="selFilter">'
                html += '<select id="' + data[i].itemCode + '" name="' + data[i].itemCode + '" class="selFilter">'
                html += '<option value=""></option>'
                html += '</select>'
                html += '</div>'
                html += '</div>'
                html += '</div>'

            }
        }
        html += '<div class="layui-form-item">'
        html += '<div class="layui-input-block">'
        html += '<button class="layui-btn" lay-submit="" lay-filter="save">立即提交</button>'
        html += '</div>'
        html += '</div>'
        $("#formData").html(html);

    });
}

function getDetail() {
    var groupId = g_getQueryString("id");
    var availablePayInfo = '';
    $.ajax({
        type: "get",
        url: "/config/group/available",
        async: false,
        success: function (data) {
            availablePayInfo = data.data
        }
    });
    $.ajax({
        type: "get",
        url: "/config/group/find/" + groupId,
        data: {},
        success: function (data) {
            if (data.code == 0) {
                $("#name").val(data.data.name);
                $("#id").val(data.data.id);
                //  debugger;
                var initVal = {};
                for (var i = 0 in availablePayInfo) {
                    if (!isNaN(i)) {
                        var payInfo = availablePayInfo[i];
                        $("#" + payInfo.itemCode).append(
                            "<option value=" + payInfo.itemCode + "&" + payInfo.paymentName + "&" + payInfo.id + ">"
                            + payInfo.paymentName
                            + "</option>");
                    }
                }
                renderForm();
                initFormVal(data.data);
            }
        }
    });
}

function renderForm() {
    layui.use('form', function () {
        var form = layui.form;
        form.render();
    });
}

function initFormVal(initVal) {
    layui.use('form', function () {
        var form = layui.form;
        form.val('mainForm', initVal);
    });
}
var token = getCookie("token");
layui.use(['form', 'layedit', 'laydate'],
    function () {
        var form = layui.form, layer = layui.layer, layedit = layui.layedit, laydate = layui.laydate;
        //监听提交
        form.on('submit(save)', function (data) {
            var formdata = data.field
            if (formdata) {
                var values = "";
                var selecter = $(".selFilter");
                for (var i = 0; i < selecter.length; i++) {
                    if (!isNaN(i)) {
                        var sel = $(selecter[i]);
                        var val = sel.val();
                        if (val) {
                            if (i == 0) {
                                values += val;
                            } else {
                                values += "," + val;
                            }
                        }
                    }
                }
                formdata.strValues = values;
                $.ajax({
                    type: "post",
                    url: "/config/group/upd/" + formdata.id,
                    headers: {'X-CSRF-TOKEN': token},
                    data: formdata,
                    success: function (data) {
                        layer.msg(data.message);
                        if (data.code == 200) {
                            setTimeout(
                                function () {
                                    var index = parent.layer.getFrameIndex(window.name); //先得到当前iframe层的索引
                                    parent.layer.close(index); //再执行关闭
                                    window.parent.location.reload();
                                },
                                1000);
                        }
                    }
                });
            }
            return false;
        });
    });
