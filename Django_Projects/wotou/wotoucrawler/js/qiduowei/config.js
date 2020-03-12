var WWW_URL = 'http://www.qiduowei.com';
var UPLOAD_URL = 'http://www.qiduowei.com/upload';
var ASSETS_URL = 'http://assets.qiduowei.com';
var IMAGE_URL = 'http://images.qiduowei.com';

$(function(){
	$(".nav-search .cate a").each(function(){
		if($(this).hasClass("active")) {
			$(".nav-search .search-head span").text($(this).data("name"));
			return false;
		}
	});
	$(".nav-search .cate a").click(function(){
		if($(this).hasClass("active")) {
			return;
		}
		var tip = '';
        if($(this).data("id") == 0) {
            tip = '请输入关键词查询企业';
        } else if($(this).data("id") == 1) {
            tip = '请输入公司名称';
        }else if($(this).data("id") == 2) {
            tip = '请输入 注册号（统一社会信用代码）';
        }else if($(this).data("id") == 3) {
            tip = '请输入法人(股东)';
        }else if($(this).data("id") == 4) {
            tip = '请输入营业范围';
        }
        $('.nav-input').attr('placeholder',tip);
		$('.nav-search .cate a').removeClass('active');
		$(this).addClass('active');
		$('.nav-search .search-head span').text($(this).data('name'));
	});
	$(".nav-search .search-head").click(function(){
		$(".nav-search .cate").css({"display":"block"});
		$('.nav-search .search-head i').removeClass("down");
		$('.nav-search .search-head i').addClass("up");
	});
	$(".nav-search .cate").hover(function(){},function(){
		$(".nav-search .cate").css({"display":"none"});
		$('.nav-search .search-head i').removeClass("up");
		$('.nav-search .search-head i').addClass("down");
	});
	$(".nav-search .search-btn").click(function(){
        var key = $(".nav-search .nav-input").val();
        var cate = $(".nav-search .cate .active").data("id");
        if(key == "") {
            return;
        }
        var url = "/search?key=" + key;
        if(cate != 0) {
            url = url + "&cate=" + cate;
        }
        window.location.href = url;
    });
    //enter键提交搜索
    document.onkeydown = function(event_e){
        if(window.event) {
            event_e = window.event;
        }

        var int_keycode = event_e.charCode||event_e.keyCode;
        if( int_keycode == '13' ) {
            $('.nav-search .search-btn').trigger('click');
            return false;
        }
    }
	//登陆
	$(document).on('click','.btn-login',function() {
		var html = $('#modal-login').html();
		if(html == '') {
			html = '<!-- 登陆 -->'+
					'<div class="modal fade" id="loginModal" tabindex="-1" role="dialog" aria-labelledby="loginModal" aria-hidden="true" data-backdrop="static">'+
						'<div class="modal-dialog">'+
							'<div class="modal-content">'+
							'<div class="modal-header">'+
								'<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
								'<h4 class="modal-title" id="myModalLabel">登陆 <small>企多维</small></h4>'+
							'</div>'+
							'<div class="modal-body">'+
								'<form action="index/user/login" method="POST" class="form-horizontal">'+
									'<div class="form-group">'+
										'<label class="col-md-3 col-xs-3 control-label">用户名:</label>'+
										'<div class="col-md-8 col-xs-8">'+
											'<input type="text" name="form[username]" value="" class="form-control" placeholder="请输入您的用户名" autocomplete="off">'+
										'</div>'+
									'</div>'+
									'<div class="form-group">'+
										'<label class="col-md-3 col-xs-3 control-label">密码:</label>'+
										'<div class="col-md-8 col-xs-8">'+
											'<input type="password" name="form[password]" value="" class="form-control" placeholder="请输入您的密码">'+
										'</div>'+
									'</div>'+
									'<div class="form-group form-group-verify hide">'+
										'<label class="col-md-3 col-xs-3 control-label">验证码:</label>'+
										'<div class="col-md-4 col-xs-4">'+
											'<input type="text" name="form[verify]" class="form-control" placeholder="">'+
										'</div>'+
										'<div class="col-md-4 col-xs-4">'+
											'<a href="javascript:void(0);" class="change-verify-image" title="看不清? 点击换一张"><img src="index/index/verify" alt="验证码图片" /></a>'+
										'</div>'+
									'</div>'+
									'<div class="form-group">'+
										'<label class="col-md-3 col-xs-3 control-label sr-only">记住密码</label>'+
										'<div class="col-md-8 col-xs-8">'+
											'<div class="checkbox">'+
												'<label><input type="checkbox" name="form[remeber]" value="1"> 记住密码</label>'+
											'</div>'+
										'</div>'+
									'</div>'+
									'<div class="form-group">'+
										'<label class="control-label sr-only">操作</label>'+
										'<div class="col-md-3 col-xs-3 col-md-offset-3 col-xs-offset-3">'+
											'<input type="hidden" id="login_reload" value="1">'+
											'<input type="submit" value="立即登陆" class="btn btn-primary login-btn">'+
										'</div>'+
										'<div class="col-md-5 col-xs-5">'+
											'<div class="form-control-static login-notice">'+
												'<span class="text-success">&nbsp;</span>'+
												'<span class="text-danger">&nbsp;</span>'+
											'</div>'+
										'</div>'+
									'</div>'+
								'</form>'+
							'</div>'+
							'<div class="modal-footer">'+
								'<a href="#" class="go2register">还没有账号? 立即注册</a>'+
							'</div>'+
							'</div>'+
						'</div>'+
					'</div>';
			$('#modal-login').html(html);
		}
		$('#loginModal').modal('show');
		return;
	});
	$(document).on('click','.login-btn',function() {
		var that = $(this);
		var form = $(this).parents('form');
		var notice = form.find('.login-notice');

		// 登陆后重载页面
		var login_reload = $('#login_reload').val();

		that.val('登陆中....');
		notice.find('.text-danger').html('&nbsp;');
		notice.find('.text-success').html('&nbsp;');

		$.post(form.attr('action'), form.serializeArray(), function(ret) {
			if(ret.status == 1) {
				notice.find('.text-danger').html('&nbsp;');
				notice.find('.text-success').html(ret.message);
				if(login_reload == 1) {
					window.location.reload();
				} else {
					$('#loginModal').modal('hide');
				}
			} else {
				that.val('立即登陆');
				notice.find('.text-danger').html(ret.message);
				notice.find('.text-success').html('&nbsp;');
				if(ret.data && ret.data.check_count >= 3) {
					$('.form-group-verify').removeClass('hide');
				}
			}
		}, 'JSON');
		return false;
	});
	// 退出
	$('.logout-btn').click(function() {
		if(!confirm('确定退出企多维吗?')) return false;

		var that = this;
		$.post($(this).data('href'), {}, function(ret) {
			if(ret.status == 1) {
				if($(that).data('location')) {
					window.location.href = $(that).data('location');
				} else {
					window.location.reload();	
				}
			} else {
				alert('退出失败, 请稍后再试');
				return false;
			}
		}, 'JSON');
		return false;
	});
	// 注册
	$(document).on('click','.register-btn',function() {
		var that = $(this);
		var form = $(this).parents('form');
		var notice = form.find('.register-notice');

		// 登陆后重载页面
		var register_reload = $('#register_reload').val();

		that.val('注册中....');
		notice.find('.text-danger').html('&nbsp;');
		notice.find('.text-success').html('&nbsp;');

		$.post(form.attr('action'), form.serializeArray(), function(ret) {
			if(ret.status == 1) {
				notice.find('.text-danger').html('&nbsp;');
				notice.find('.text-success').html(ret.message);
				window.setTimeout(function() {
					if(register_reload == 1) {
						window.location.reload();
					} else {
						$('#loginModal').modal('hide');
					}
				}, 1000);
			} else {
				that.val('立即注册');
				notice.find('.text-danger').html(ret.message);
				notice.find('.text-success').html('&nbsp;');
			}
		}, 'JSON');
		return false;
	});
	//注册
	$(document).on('click','.btn-register',function() {
		var html = $('#modal-register').html();
		if(html == '') {
			html = '<!-- 注册 -->'+
					'<div class="modal fade" id="registerModal" tabindex="-1" role="dialog" aria-labelledby="registerModal" aria-hidden="true" data-backdrop="static"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button><h4 class="modal-title" id="myModalLabel">注册 <small>企多维</small></h4></div><div class="modal-body"><form action="index/user/register" method="POST" class="form-horizontal"><div class="form-group"><label class="col-md-3 col-xs-3 control-label">用户名</label><div class="col-md-8 col-xs-8"><input type="text" name="form[username]" class="form-control" placeholder="请输入您的常用邮箱账号"></div></div><div class="form-group"><label class="col-md-3 col-xs-3 control-label">密码</label><div class="col-md-8 col-xs-8"><input type="password" name="form[password]" class="form-control" placeholder="长度范围: 6-20位"></div></div><div class="form-group"><label class="col-md-3 col-xs-3 control-label">重复密码</label><div class="col-md-8 col-xs-8"><input type="password" name="form[repassword]" class="form-control" placeholder="请再输入一次密码"></div></div><hr><div class="form-group"><label class="col-md-3 col-xs-3 control-label">您的姓名</label><div class="col-md-8 col-xs-8"><input type="text" name="form[truename]" class="form-control" placeholder="可选"></div></div><div class="form-group"><label class="col-md-3 col-xs-3 control-label">您的手机号</label><div class="col-md-8 col-xs-8"><input type="text" name="form[phone]" class="form-control" placeholder="可选"></div></div><div class="form-group"><label class="col-md-3 col-xs-3 control-label">您的QQ号</label><div class="col-md-8 col-xs-8"><input type="text" name="form[qq]" class="form-control" placeholder="可选"></div></div><div class="form-group hidden"><label class="col-md-3 col-xs-3 control-label sr-only">用户协议</label><div class="col-md-8 col-xs-8"><div class="checkbox"><label><input type="checkbox" name="form[agreement]" value="1"> 我已阅读并遵守大海洋相关用户协议</label><a href="index/help?id=8" target="_blank">查看用户协议</a></div></div></div><div class="form-group"><label class="col-md-3 col-xs-3 control-label">验证码:</label><div class="col-md-4 col-xs-4"><input type="text" name="form[verify]" class="form-control"><input type="hidden" name="form[level]" value="5" class="form-control"></div><div class="col-md-4 col-xs-4"><a href="#" class="change-verify-image" title="看不清? 点击换一张"><img src="index/index/verify" /></a></div></div><div class="form-group"><label class="control-label sr-only">操作:</label><div class="col-md-3 col-xs-3 col-md-offset-3"><input type="hidden" id="register_reload" value="1"><input type="submit" value="立即注册" class="btn btn-primary register-btn"></div><div class="col-md-5 col-xs-5"><div class="form-control-static register-notice"><span class="text-success">&nbsp;</span><span class="text-danger">&nbsp;</span></div></div></div></form></div><div class="modal-footer"><a href="#" class="go2login">已有账号? 立即登陆</a></div></div></div></div>';
			$('#modal-register').html(html);
		}
		$('#registerModal').modal('show');
		return;
	});
	// 去注册
	$(document).on('click','.go2register',function() {
		$('#loginModal').modal('hide');
		window.setTimeout(function() {
			$('.btn-register').trigger('click');
		}, 500);
		return false;
	});

	// 去登陆
	$(document).on('click','.go2login',function() {
		$('#registerModal').modal('hide');
		window.setTimeout(function() {
			$('.btn-login').trigger('click');
		}, 500);
		return false;
	});
	// 切换验证码
	$(document).on('click','.change-verify-image', function() {
		var src = $(this).find('img').attr('src');
		if(src.indexOf('rnd=') == -1) {
			if(src.indexOf('?') != -1) {
				src += '&rnd='+ new Date().getTime();
			} else {
				src += '?rnd='+ new Date().getTime();    
			}
		} else {
			src = src.replace(/rnd=[\d.]+/, 'rnd='+ new Date().getTime());
		}
		$(this).find('img').attr({
			'src': src,
		});
		return false;
	});

	//侧边帮助栏
	$(window).scroll(function() {
		if ($(window).scrollTop() > 100) {
			$(".help-left-list").fadeIn();
		} else {
			$(".help-left-list").fadeOut();
		}
	});
	$(".help-left-list .backtop").click(function() {
		$('body, html').animate({scrollTop: 0});
		return false;
	});
	$(".help-left-list .weixin").hover(function(){
		$(".help-left-weixin-hover").css({"display":"block"});
	},function(){
		$(".help-left-weixin-hover").css({"display":"none"});
	});
});

/** 搜索结果html**/
function dealInfoToHTML(ret){
	var html = "";
	var len = ret.data.length;
	for(var i = 0;i < len; i++){
		html = html + '<a href="/detail-'+ret.data[i]['id']+'" target="_blank"><span>'+ret.data[i]['category']+'</span>'+ret.data[i]['company']+'</a>';
	}
	return html;
}
// 搜索Suggest
function suggestList(key,cate){
	$("#suggest-list").hide();
	if (cate == 0 || cate == 1) {
		$.ajax({
			type: "POST",
			url: '/suggest',
			dataType: "json",
			data: {"keyword":key,"cate":cate},
			success: function (ret) {
				html = "";
				if (ret.status) {
					var html = dealInfoToHTML(ret);

					$("#suggest-list").show();
					$("#suggest-list").html(html);
				}

			}
		});
	}

	return true;
}
//格式化公司网址
function formatUrl(url) {
	if(url == "") return "";
	url = url.toLowerCase();
	if(url.indexOf("http://") < 0) {
		url = "http://" + url;
	}
	if(!(url.indexOf(",") < 0)) {
		var arr = url.split(",");
		url = arr[0];
	} else if(!(url.indexOf("，") < 0)) {
		var arr = url.split("，");
		url = arr[0];
	}
	return url;
}$(function(){
    $("#suggest-list").hide();

    var typingTimer;
    var suggestInterval = 200;

    $('#nav-input').keyup(function(){
        clearTimeout(typingTimer);
        var cate = $(".nav-search .cate .active").data("id");console.log(cate);
        var suggestVal = $.trim($('#nav-input').val());console.log(suggestVal);
        if (suggestVal != "" && suggestVal.length > 1) {
            typingTimer = setTimeout(suggestList(suggestVal,cate), suggestInterval);
        }
    });
    $("#nav-input").click(function(){
        var cate = $(".nav-search .cate .active").data("id");
        if (cate == 0 || cate == 1) {
            if ($("#suggest-list").html() != '') {
                $("#suggest-list").show();
            } else {
                var suggestVal = $.trim($('#nav-input').val());
                if (suggestVal != "" && suggestVal.length > 1) {
                    suggestList(suggestVal,cate);
                }
            }
        }

    });

    document.onclick=function(e){
        var e=e?e:window.event;
        var tar = e.srcElement||e.target;
        if(tar.id!="nav-input") {
            $("#suggest-list").hide();
        }
    }
});
$(function(){
    var loadingHtml = '<div class="loading"><img width="60" alt="" src="'+ ASSETS_URL +'/www/v1/images/common/loading.gif"></div>';

    if(!($(".user .login").html() == null)) {
        var tel = $(".telephone").text().replace(/\s/g, "");
        $(".telephone").html('<i class="tel"></i>'+tel.substr(0,tel.length - 4)+"****"+'<a href="javascript:;" class="btn-login">登录看完整</a>');
    }
    var web = $(".website").text().replace(/\s/g, "");
    if(web != null) {
        $(".website").html('<i class="web"></i><a href="'+formatUrl(web)+'" target="_blank" rel="nofollow">'+web+'</a>');
    }
    //启信报告
    $('.send-report').click(function(){
        $("#mask").css("height",$(document).height());
        $("#mask").show();
        $("body").addClass('modal-open');
        $("body").css("margin-right","17px");
        $(".report-modal").css({"display":"block"});
    });
    $('.report-cancel').click(function(){
        $("#mask").hide();
        $("body").removeClass('modal-open');
        $("body").css("margin-right","0");
        $(".report-modal").css({"display":"none"});
    });
    $(".report-modal .send").click(function(){
        var email = $(".report-email").val();
        if(email == "") {
            alert('请输入接受企信报告的邮箱');
        }
    });

    //信息反馈
    $(".feedback a").click(function(){
        $("#mask").css("height",$(document).height());
        $("#mask").show();
        $("body").addClass('modal-open');
        $("body").css("margin-right","17px");
        $(".feedback-modal").css({"display":"block"});
    });
    $(".feedback-cancel").click(function(){
        $("#mask").hide();
        $("body").removeClass('modal-open');
        $("body").css("margin-right","0");
        $(".feedback-modal").css({"display":"none"});
    });
    $(".feedback-submit").click(function(){
        var content = $(".feedback-content").val();
        var tel = $(".feedback-tel").val();
        var verify = $(".verify-code").val();
        var mobile = /^1\d{10}$/;
        var phone = /^0\d{2,3}-?\d{7,8}$/;
        var email = /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
        var verifyReg = /^[a-zA-Z0-9]{4}/;
        if(content == "") {
            $(".feedback-content").siblings("p").text("反馈内容不能为空");
            return false;
        }
        if(tel == "") {
            $(".feedback-content").siblings("p").text("联系方式不能为空");
            return false;
        }
        if(!mobile.test(tel) && !email.test(tel) && !phone.test(tel)) {
            $(".feedback-tel").siblings("p").text("联系方式格式不正确");
            return false;
        }
        if(verify == "") {
            $(".verify-code").siblings("p").text("验证码不可为空");
            return false;
        }
        if(!verifyReg.test(verify)) {
            $(".verify-code").siblings("p").text("验证码格式不正确");
            return false;
        }
        $.ajax({
            type: "POST",
            url: '/feedback',
            dataType: "json",
            data: {"content":content,"tel":tel,"verify":verify,"url":window.location.href,"note":company},
            success: function (ret) {
                if (ret.status) {
                    $(".feedback-modal .bottom-item span").css({"display":"inline-block"});
                    setTimeout(function(){$(".feedback-cancel").trigger("click");},3000);
                } else  {
                    if(ret.message == "验证码错误") {
                       $(".verify-code").siblings("p").text("验证码错误");
                       $(".feedback-modal .change-verify-image").trigger("click");
                        return false; 
                    } else {
                        alert(ret.message);
                        return false; 
                    }
                }
            }
        });
        return true;
    });
    $(".feedback-content").focusin(function(){
        $(".feedback-content").siblings("p").text("");
        return true;
    });
    $(".feedback-tel").focusin(function(){
        $(".feedback-tel").siblings("p").text("");
        return true;
    });
    $(".verify-code").focusin(function(){
        $(".verify-code").siblings("p").text("");
        return true;
    });

	//股东信息左右切换
    if($(".shareholder-detail .title span").text() > 2) {
    	var shareholderUnslider = $('.shareholder-slider').unslider({
    		autoplay: false,
            dots: true,
        });
    }
    $('.shareholder-slider .unslider-arrow-sub').click(function() {
        var fn = this.className.split(' ')[1];
        shareholderUnslider.data('unslider')[fn]();
    });

    //内容页导航栏
    $('.content-nav a').click(function(){
    	if($(this).hasClass('active')) {
    		return;
    	}
    	$('.content-nav a').removeClass('active');
    	$(this).addClass('active');
    });
    var bodyWidth = $(document.body).width();
    var divWidth = $('.detail-content').width();
    var leftWidth = ((bodyWidth - divWidth) / 2) + 15;
    $(window).scroll(function() {
        if($(window).scrollTop() > 430) {
            $('.content-nav').css({'position':'fixed','left':0,'top':0,'padding-left':leftWidth,'z-index':'11'});
        } else {
            $('.content-nav').css({'position':'relative','padding-left':'15px'});
        }
    });

    //模态框
    $(".detail-modal .cancel").click(function(){
        hideDetailModal();
    });
    // $(".justic-info a").click(function(){
    //     showDetailModal();
    // });

    var company = $("#company-name").text();
    var verticalPagesize = 3;
    var horizontalPagesize = 2;

    //变更信息分页
    var change_count = $('.change-detail .title span').text();
    if(change_count != '' && change_count != null && change_count > verticalPagesize) {
        $("#change_page").createPage({
            pageCount: Math.ceil(change_count/verticalPagesize),
            current:1,
            backFn:function(p){
                $('.change-detail .list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getChangeMessagePaging',
                    dataType: "json",
                    data: {"p":p,"id":$(".compay-id").text()},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="list-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="change-info">'+
                                                    '<p class="first">变更项目：'+ret.data[i][1]+'</p>'+
                                                    '<p>变更日期：'+ret.data[i][0]+'</p>'+
                                                    '<p>变更前：'+ret.data[i][2]+'</p>'+
                                                    '<p>变更后：'+ret.data[i][3]+'</p>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.change-detail .list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#change_page").hide();
    }

    //裁判文书分页
    var justic_count = $('.justic-detail .title span').text();
    if(justic_count != '' && justic_count != null && justic_count > verticalPagesize) {
        $("#justic_page").createPage({
            pageCount: Math.ceil(justic_count/verticalPagesize),
            current:1,
            backFn:function(p){
                $('.justic-detail .list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getJusticPaging',
                    dataType: "json",
                    data: {"p":p,"name":company},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="list-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="justic-info">'+
                                                    '<p><a href="javascript:;" title="'+ret.data[i]['CaseName']+'" data-id="'+ret.data[i]['id']+'">'+ret.data[i]['CaseName']+'</a></p>'+
                                                    '<p>法院：'+ret.data[i]['CourtName']+'</p>'+
                                                    '<p>案号：'+ret.data[i]['CaseNo']+'</p>'+
                                                    '<p>裁判日期：'+ret.data[i]['TrialDate']+'</p>'+
                                                    '<p class="justic-state">'+ret.data[i]['TrialRound']+'</p>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.justic-detail .list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#justic_page").hide();
    }

    //法院裁判书
    $(document).on('click',".justic-detail .justic-info a",function(){
        var key = $(this).data('id');
        $('.justic-modal .content').append(loadingHtml);
        showDetailModal('.justic-modal');
        $.ajax({
            type: "POST",
            url: '/index/detail/getJustic',
            dataType: "json",
            data: {"key":key},
            success: function (ret) {
                if (ret.status) {
                    $('.juctic-info .title').text(ret.data.CaseName);
                    $('.juctic-info .publicDate').text(ret.data.PubDate);
                    $('.juctic-info .name').text(ret.data.CourtName);
                    $('.juctic-info .caseNo').text(ret.data.CaseNo);
                    $('.justic-desc').html(ret.data.Ugc);
                    $('.justic-modal .content .loading').remove();
                    $('.justic-modal .content .justic-content').removeClass('hide');
                } else {
                    alert(ret.message);
                }
            }
        });
        return false;
    });

    //商标分页
    var trademark_count = $('.trademark-detail .title span').text();
    if(trademark_count != '' && trademark_count != null && trademark_count > verticalPagesize) {
        $("#trademark_page").createPage({
            pageCount: Math.ceil(trademark_count/verticalPagesize),
            current:1,
            backFn:function(p){
                $('.trademark-detail .list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getTrademakePaging',
                    dataType: "json",
                    data: {"p":p,"name":company},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="list-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="thumb"><img src="'+ret.data[i]['Logo']+'" alt=""></div>'+
                                                '<div class="trademark-info">'+
                                                    '<div class="company-name"><a href="javascript:;" title="'+ret.data[i]['RegisterName']+'" data-id="'+ret.data[i]['ddid']+'" class="brand-detail">'+ret.data[i]['RegisterName']+'</a><span class="brand-detail"  data-id="'+ret.data[i]['ddid']+'">更多信息</span></div>'+
                                                    '<div class="info">'+
                                                    '<p>类别号：'+ret.data[i]['NationCat']+'</p>'+
                                                    '<p>申请日期：'+ret.data[i]['ApplyDate']+'</p>'+
                                                    '</div>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.trademark-detail .list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#trademark_page").hide();
    }

    //商标详情
    $(document).on('click',".trademark-detail .brand-detail",function(){
        var key = $(this).data('id');
        $('.brand-modal .content').append(loadingHtml);
        showDetailModal('.brand-modal');
        $.ajax({
            type: "POST",
            url: '/index/detail/getTrademake',
            dataType: "json",
            data: {"key":key},
            success: function (ret) {
                if (ret.status) {
                    $('.brand-modal .owner a').text(ret.data.ApplyCN);
                    $('.brand-modal .proxy a').text(ret.data.Proxy);
                    $('.brand-modal .info .name a').text(ret.data.RegisterName);
                    $('.brand-modal .info .status a').text(ret.data.Status);
                    $('.applyAdd label').text(ret.data.ApplyAddressCN);
                    $('.type label').text(ret.data.Type);
                    $('.share label').text(ret.data.Share);
                    $('.firstDate label').text(ret.data.FirstNoDate);
                    $('.specialDate label').text(ret.data.SpecialDate);
                    $('.unitNo label').text(ret.data.NationCat);
                    $('.regNo label').text(ret.data.RegisterNum);
                    $('.regDate label').text(ret.data.ApplyDate);
                    $('.brand-flow label').html(ret.data.Workflow);
                    $('.goods-service-list label').html(ret.data.Product);
                    $('.brand-modal .content .loading').remove();
                    $('.brand-modal .content .brand-content').removeClass('hide');
                    $('#thumb').attr('src',ret.data.Logo);
                } else {
                    alert(ret.message);
                }
            }
        });
        return false;
    });

    //软件著作权分页
    var softregister_count = $('.softregister-detail .title span').text();
    if(softregister_count != '' && softregister_count != null && softregister_count > horizontalPagesize) {
        $("#softregister_page").createPage({
            pageCount: Math.ceil(softregister_count/horizontalPagesize),
            current:1,
            backFn:function(p){
                $('.softregister-detail .softregister-list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getSoftregisterPaging',
                    dataType: "json",
                    data: {"p":p,"name":company},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="softregister-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="softregister-info">'+
                                                    '<p class="first">软件全称：'+ret.data[i]['SoftName']+'</p>'+
                                                    '<p>登记号：'+ret.data[i]['RegisterNo']+'</p>'+
                                                    '<p>分类号：'+ret.data[i]['CategoryNo']+'</p>'+
                                                    '<p>版本号：'+ret.data[i]['VersionNo']+'</p>'+
                                                    '<p>首次发表日期：'+ret.data[i]['PublicDate']+'</p>'+
                                                    '<p>登记批准日期：'+ret.data[i]['RegisterDate']+'</p>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.softregister-detail .softregister-list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#softregister_page").hide();
    }

    //专利分页
    var patent_count = $('.patent-detail .title span').text();
    if(patent_count != '' && patent_count != null && patent_count > horizontalPagesize) {
        $("#patent_page").createPage({
            pageCount: Math.ceil(patent_count/horizontalPagesize),
            current:1,
            backFn:function(p){
                $('.patent-detail .patent-list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getPatentPaging',
                    dataType: "json",
                    data: {"p":p,"name":company},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="patent-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="patent-info">'+
                                                    '<p><a href="javascript:;" title="'+ret.data[i]['PatentName']+'" data-id="'+ret.data[i]['id']+'">'+ret.data[i]['PatentName']+'</a></p>'+
                                                    '<p>专利类型：'+ret.data[i]['PatentType']+'</p>'+
                                                    '<p>发布日期：'+ret.data[i]['ApplyPublicDate']+'</p>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.patent-detail .patent-list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#patent_page").hide();
    }

     //域名分页
    var domain_count = $('.domain-detail .title span').text();
    if(domain_count != '' && domain_count != null && domain_count > horizontalPagesize) {
        $("#domain_page").createPage({
            pageCount: Math.ceil(domain_count/horizontalPagesize),
            current:1,
            backFn:function(p){
                $('.domain-detail .domain-list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getDomainPaging',
                    dataType: "json",
                    data: {"p":p,"key":$(".compay-id").text()},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="domain-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="domain-info">'+
                                                    '<p class="first">网址：'+ret.data[i]['domains']+'</p>'+
                                                    '<p>网站名称：'+ret.data[i]['sitename']+'</p>'+
                                                    '<p>备案/许可证号：'+ret.data[i]['icp']+'</p>'+
                                                    '<p>审核时间：'+ret.data[i]['check_date']+'</p>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.domain-detail .domain-list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#domain_page").hide();
    }

    //专利详情
    $(document).on('click',".patent-info a",function(){
        var key = $(this).data('id');
        $('.patent-modal .content').append(loadingHtml);
        showDetailModal('.patent-modal');
        $.ajax({
            type: "POST",
            url: '/index/detail/getPatent',
            dataType: "json",
            data: {"key":key},
            success: function (ret) {
                if (ret.status) {
                    $('.patent-content .title').text(ret.data.PatentName);
                    $('.patent-content .aplyNo label').text(ret.data.ApplyNumber);
                    $('.patent-content .publishDate label').text(ret.data.ApplyDate);
                    $('.patent-content .publicNo label').text(ret.data.ApplyPublicNumber);
                    $('.patent-content .publicDate label').text(ret.data.ApplyPublicDate);
                    $('.patent-content .creator label').text(ret.data.Inventor);
                    $('.patent-content .preferNo label').text(ret.data.Priority);
                    $('.patent-content .type label').text(ret.data.PatentType);
                    $('.patent-content .cateNo label').text(ret.data.CategoryNo);
                    $('.patent-content .PatentAgency label').text(ret.data.PatentAgency);
                    $('.patent-content .Agencer label').text(ret.data.Agencer);
                    $('.patent-content .patent-desc').text(ret.data.Berief);
                    $('.patent-modal .content .loading').remove();
                    $('.patent-modal .content .patent-content').removeClass('hide');
                    $('#patent-thumb').attr('src',ret.data.Logo);
                } else {
                    alert(ret.message);
                }
            }
        });
        return false;
    });

    //对外投资分页
    var invest_count = $('.invest-detail .title span').text();
    if(invest_count != '' && invest_count != null && invest_count > verticalPagesize) {
        $("#invest_page").createPage({
            pageCount: Math.ceil(invest_count/verticalPagesize),
            current:1,
            backFn:function(p){
                $('.invest-detail .list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getInvestPaging',
                    dataType: "json",
                    data: {"p":p,"name":company},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="list-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="invest-info">'+
                                                    '<p><a href="/detail-'+ret.data[i]['id']+'" title="'+ret.data[i]['CompanyName']+'" target="_blank">'+ret.data[i]['CompanyName']+'</a></p>'+
                                                    '<p>'+
                                                        '<span class="boss">法人代表：'+ret.data[i]['Boss']+'</span>'+
                                                        '<span class="money">注册资本：'+ret.data[i]['RegisterMoney']+'</span>'+
                                                        '<span> 成立日期：'+ret.data[i]['Date']+'</span>'+
                                                    '</p>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.invest-detail .list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#invest_page").hide();
    }

    //经营异常分页
    var registerNum = $(".registerNum").text();
    var socialCreditCode = $(".socialCreditCode").text();
    var manage_count = $('.manage-detail .title span').text();
    if(manage_count != '' && manage_count != null && manage_count > verticalPagesize) {
        $("#manage_page").createPage({
            pageCount: Math.ceil(manage_count/verticalPagesize),
            current:1,
            backFn:function(p){
                $('.manage-detail .list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getExceptionPaging',
                    dataType: "json",
                    data: {"p":p,"registerNum":registerNum,"socialCreditCode":socialCreditCode,},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="list-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="manage-info">'+
                                                    '<p>列入原因：'+ret.data[i]['AbnormalReason']+'</p>'+
                                                    '<p>列入日期：'+ret.data[i]['AddDate']+' </p>'+
                                                    '<p>移出原因：'+ret.data[i]['NormalReason']+'</p>'+
                                                    '<p>移出日期：'+ret.data[i]['OutDate']+'</p>'+
                                                    '<p class="organ">'+ret.data[i]['AddOrgan']+'</p>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.manage-detail .list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#manage_page").hide();
    }

    //微信分页
    var weixin_count = $('.weixin-detail .title span').text();
    if(weixin_count != '' && weixin_count != null && weixin_count > horizontalPagesize) {
        $("#weixin_page").createPage({
            pageCount: Math.ceil(weixin_count/10),
            current:1,
            backFn:function(p){
                $('.weixin-detail .weixin-list').append(loadingHtml);
                $.ajax({
                    type: "POST",
                    url: '/index/detail/getWeixinPaging',
                    dataType: "json",
                    data: {"p":p,"key":$(".compay-id").text(),"name":company},
                    success: function (ret) {
                        if (ret.status) {
                            var length = ret.data.length;
                            if(length > 0) {
                                var html = '';
                                for(var i=0;i<length;i++) {
                                    html += '<div class="weixin-item">'+
                                                '<div class="item">'+ret.data[i]['item']+'</div>'+
                                                '<div class="weixin-info">'+
                                                    '<p class="first">微信公众号：'+ret.data[i]['wx_name']+'</p>'+
                                                    '<p>昵称：'+ret.data[i]['wx_nickname']+'</p>'+
                                                '</div>'+
                                            '</div>';
                                }
                                $('.weixin-detail .weixin-list').html(html);
                            }
                            return;
                        } else  {
                            alert(ret.message);
                        }
                    }
                });
            }
        });
    } else {
        $("#weixin_page").hide();
    }

    //2秒后加载商标图标
    $(document).ready(function(){
        setTimeout(function() {
            var imgObs = $('.trademark-detail .list-item img');
            $.each(imgObs,function(){
                $(this).attr('src',$(this).data('src'));
            });
        }, 2000);
    });
});
//显示模态框
function showDetailModal(obj)
{
    $("#mask").css("height",$(document).height());
    $("#mask").show();
    $("body").addClass('modal-open');
    $("body").css("margin-right","17px");
    $(obj).css({
        "display":"block",
        "left": ($(window).width() - $('.detail-modal').outerWidth())/2,
        "top": ($(window).height() - $('.detail-modal').outerHeight())/2 + $(document).scrollTop()
    });
}
//关闭模态框
function hideDetailModal()
{
    $("#mask").hide();
    $("body").removeClass('modal-open');
    $("body").css("margin-right","0");
    $(".detail-modal").css({
        "display":"none",
        "left":0,
        "right":0
    });
}

function closeHTML(str){
    var arrTags=["span","tr","td","li","ul","table","div","section"];
    for(var i=0;i<arrTags.length;i++){
        var intOpen=0;
        var intClose=0;
        var re=new RegExp("\\<"+arrTags[i]+"( [^\\<\\>]+|)\\>","ig");
        var arrMatch=str.match(re);
        if(arrMatch!=null) intOpen=arrMatch.length;
        re=new RegExp("\\<\\/"+arrTags[i]+"\\>","ig");
        arrMatch=str.match(re);
        if(arrMatch!=null) intClose=arrMatch.length;
        for(var j=0;j<intOpen-intClose;j++){
            str+="</"+arrTags[i]+">";
        }
    }
    return str;
}