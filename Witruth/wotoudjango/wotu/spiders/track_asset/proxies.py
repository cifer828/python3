# -*- coding:utf-8 -*-#
import requests
def abuyun_proxy():
    """
    阿布云代理
    acc：wotou
    psw：756870
    """
    # 代理服务器
    proxyHost = "proxy.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "H80235831I4P43JD"
    proxyPass = "C504B13EB040C0CC"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host" : proxyHost,
        "port" : proxyPort,
        "user" : proxyUser,
        "pass" : proxyPass,
    }
    proxies = {
        "http"  : proxyMeta,
        "https" : proxyMeta,
    }
    return proxies

def wuyou_proxy():
    """
    无忧代理
    """
    order = "2d65cf792190c55c63806da206a6152e"
    apiUrl = "http://api.ip.data5u.com/dynamic/get.html?order=" + order
    res = requests.get(apiUrl).content.strip()
    proxies = {'http':'http://%s' % res, 'https':'http://%s' % res}
    return proxies