import urllib
proxies={'https':'http://121.232.146.14:9000'}
proxy_handler = urllib.ProxyHandler(proxies)
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)