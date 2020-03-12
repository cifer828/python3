var json = '';
var fundList ;
var page = 0 ;
var size = 0;
$(function() {
    if(document.cookie.indexOf("look=first") == -1) {
        loadNoticeDialog();
        loadDataTable();
    }else{
        loadDataTable();
    }
    $('#tooggleAMACInfo').load('../tip.html');
    //	var tooltips = $("[title]").tooltip({
    //		position:{
    //			my:"left top",
    //			at:"right+5 top-5"
    //		}
    //	});

    $("body").on("keydown",function(e) {
        if(e.keyCode==13) {
            e.preventDefault();
            reload();
        }
    });

    showClickCount();

    if(!+'\v1' && !'1'[0]) {
        $("#IE67").show();
        $("#otherBrowser").hide();
    }else {
        $("#IE67").hide();
        $("#otherBrowser").show();
    }
});


//查询按钮
function reload(){
    var map = {};
    var keyword = $.trim($("#keyword").val()).replace("(", "&#40;").replace(")", "&#41;");
    var putOnRecordPhase = $.trim($("#putOnRecordPhase").val());//基金备案阶段
    var managerType = $.trim($("#managerType").val());//管理类型
    var workingState = $.trim($("#workingState").val());//运作状态

    if(keyword != ''&& keyword != '请输入基金名称、私募基金管理人名称') {
        map["keyword"] = keyword;
    }
    if(putOnRecordPhase != ''){
        map['putOnRecordPhase'] = putOnRecordPhase;
    }
    if(managerType != ''){
        map['managerType'] = managerType;
    }
    if(workingState != ''){
        map['workingState'] = workingState;
    }
    fundList.fnSettings().sAjaxSource = "/amac-infodisc/api/pof/fund?rand="+Math.random();
    json = JSON.stringify(map);
    if(json=='{}') {
        json = '';
    }
    $("#fundlist").dataTable().fnDraw();
}

function openAMACInfo(){
    $("#tooggleAMACInfo").toggle();
};

function loadDataTable(){
    fundList = $('#fundlist').dataTable( {
        "bPaginate" : true,
        'sPaginationType': 'ellipses',
        "bLengthChange" : true,
        "bFilter" : false,
        "bInfo" : true,
        "ordering" :false,
        "bAutoWidth" : false,
        "bProcessing": false,
        "aLengthMenu" : [[20,10,50,100],[20,10,50,100]],
        "sDom" : '<"top">t<"bottom"ilp>',
        "bServerSide": true,
        "sAjaxSource": "/amac-infodisc/api/pof/fund?rand="+Math.random(),
        "fnServerData" : function(sSource,aoData,fnCallback){
            if(json == '') {
                json = "{}";
            }

            $.each(aoData,function(i,item){
                if(item.name=='iDisplayStart'){
                    page = parseInt(item.value);
                }else if(item.name=='iDisplayLength'){
                    size = parseInt(item.value);

                }
            });

            page = parseInt(page/size);
            sSource += "&page="+page;
            sSource += "&size="+size;

            $.ajax({
                type : "post",
                contentType : "application/json",
                url : sSource,
                dataType : "json",
                data : json.replace("[","").replace("]",""),
                success : function(resp){
                    var data = [];
                    data.aaData = resp.content;
                    data.sEcho = "";
                    data.iTotalRecords = resp.totalElements;
                    data.iTotalDisplayRecords = resp.totalElements;
                    $.each(data.aaData,function(i,item){
                        item.no = i+1;
                    });
                    fnCallback(data);
                    //console.log(JSON.stringify(aoData));
                },
                error:function(msg){
                    alert("查询失败，请与系统管理员联系！");
                }

            });
        },
        "oLanguage" :{
            "sLengthMenu" : "显示_MENU_条",
            "sZeroRecords" : "没有相关记录",
            "sInfo" : "共 _TOTAL_ 条记录，共_PAGES_页",
            "sInfoEmpty" : "没有数据",
            "sInfoFiltered" : "(从_MAX_条数据中检索)",
            "oPaginate" : {
                "sFirst" : "首页",
                "sPrevious" : "上一页",
                "sNext" : "下一页",
                "sLast" : "末页"
            }
        },
        "aoColumns": [
        {"mDataProp" : 'no' , "sClass" : "center","bSearchable" : false, "bSortable":false },
        {"mDataProp" : 'fundName' , "sClass" : "center","bSearchable" : false, "bSortable":false  },
        {"mDataProp" : 'managerName' , "sClass" : "center"},
        {"mDataProp" : 'establishDate' , "sClass" : "center"},
        {"mDataProp" : 'putOnRecordDate' , "sClass" : "center","bSearchable" : false, "bSortable":false }
        /*,	{"mDataProp" : 'isDeputeManage', "sClass" : "center","bSearchable" : false, "bSortable":false }*/
        ],
        "createdRow": function ( row, data, index ) {
            if(data.id!=null){
                if(data.lastQuarterUpdate==true){
                    $(row).find('td:eq(1)').html('<a class="ajaxify" href="'+data.url+'" target="_blank"><font color=red>*</font>'+data.fundName+'</a>');
                }else{
                    $(row).find('td:eq(1)').html('<a class="ajaxify" href="'+data.url+'" target="_blank">'+data.fundName+'</a>');
                }
                $(row).find('td:eq(2)').html('<a class="ajaxify" href="'+data.managerUrl+'" target="_blank">'+data.managerName+'</a>');
            }
            if(data.establishDate!=null){
                $(row).find('td:eq(3)').html(formatDate(data.establishDate));
            }
            if(data.putOnRecordDate!=null){
                $(row).find('td:eq(4)').html(formatDate(data.putOnRecordDate));
            }
        }
    } );
}

function loadNoticeDialog(){
    $("#dialog-title").dialog({
        autoOpen:false,
        height:450,
        width:760,
        modal:true,
        draggable:true,
        resizable:false,
        closeOnEscape : false,
        open:function(){
            $(".ui-dialog-titlebar-close").hide();
        },
        create:function(){
            $("div[aria-labelledby^='ui-dialog-title-dialog-createInternation']").css(
                    "height", "auto");
            createDialogEvent();
        },
        buttons:[{
            text:'关闭',
            click:function(){
                $(this).dialog("close");
            }
        }]
    }).dialog("open");
};

function createDialogEvent(){
    $(".ui-dialog-buttonset").find("button").each(function(){
        $(this).attr("disabled",true);
        $(this).css("color","#888888");
    });
    $(".ui-widget-header").css("color","rgb(204,10,34)");
    var count = 4;
    setInterval(countDown,1000);
    function countDown(){
        $("#timeShow").html(count+" S");
        if(count==0){
            $("#timeShow").hide();
            $(".ui-dialog-buttonset").find("button").each(function(){
                $(this).attr("disabled",false);
                $(this).css("color","#555555");
            });
            document.cookie="look=first";
        }
        count--;
    }
};

//基金备案阶段
function choosePutOnRecordPhase(obj) {
    if($(obj).hasClass("active")) {
        $(obj).removeClass("active");
        $("#putOnRecordPhase").val('');
        return;
    }
    $("#putOnRecordPhase").val($(obj).attr("value"));
    $(obj).siblings().removeClass("active");
    $(obj).addClass("active");
    return false;
}

//管理类型
function chooseManagerType(obj) {
    if($(obj).hasClass("active")) {
        $(obj).removeClass("active");
        $("#managerType").val('');
        return;
    }
    $("#managerType").val($(obj).attr("value"));
    $(obj).siblings().removeClass("active");
    $(obj).addClass("active");
    return false;
}

//运作状态
function chooseWorkingState(obj) {
    if($(obj).hasClass("active")) {
        $(obj).removeClass("active");
        $("#workingState").val('');
        return;
    }
    $("#workingState").val($(obj).attr("value"));
    $(obj).siblings().removeClass("active");
    $(obj).addClass("active");
    return false;
}

//清除查询条件
function clearCondition(){
    $("#keyword").val("请输入基金名称、私募基金管理人名称");
    $("#keyword").addClass("watermark");
    $("[name='putOnRecordPhase']").removeClass("active");
    $("#putOnRecordPhase").val("");
    $("[name='managerType']").removeClass("active");
    $("#managerType").val("");
    $("[name='workingState']").removeClass("active");
    $("#workingState").val("");
}

function formatDate(time) {
    var d = new XDate(time);
    return d.toString("yyyy-MM-dd");
}

function keywordOnFocus(obj) {
    if(obj.value=='请输入基金名称、私募基金管理人名称') {
        obj.value='';
        $(obj).removeClass("watermark");
    }
}

function keywordOnBlur(obj) {
    if($.trim(obj.value) == '') {
        $(obj).addClass("watermark");
        obj.value='请输入基金名称、私募基金管理人名称';
    }
}

//更新浏览量
function showClickCount() {
    $.ajax({
        url : "/amac-infodisc/api/hits/pof/fund",
        type : "get",
        contentType: "application/json",
        success:function(data){
            if(data!=null&&data!=''){
                $("#hitsCount").html("浏览量："+data);
            }
        }
    });
}
