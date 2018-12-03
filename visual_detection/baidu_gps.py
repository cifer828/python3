import requests
import json

raw_gps = []
with open('C:/Users/zhqch/Desktop/gps.csv') as f:
    con =  f.read()
    con = con.split('\n')
    for c in con:
        r = c.split(',')
        if len(r) >= 2:
            raw_gps.append(r[2] +  ',' + r[1])
baidu_gps = []
for idx in range(0, len(raw_gps), 50):
    url1 = 'http://api.map.baidu.com/geoconv/v1/?coords='
    url2 = '&from=1&to=5&ak=uiZdiRSqbUZzD49GtHCu10srdkR7qKaC'
    for j in range(idx, min([len(raw_gps), idx + 50])):
        url1 += raw_gps[j] + ';'
    url = url1[:-1] + url2
    a = requests.get(url)
    b = json.loads(a.text)['result']
    baidu_gps += [(g['y'], g['x']) for g in b]

with open('C:/Users/zhqch/Desktop/baidu.csv', 'w') as f:
    for bg in baidu_gps:
        f.write(str(bg[0]) + ',' + str(bg[1]) + '\n')






