#-*- coding:utf-8-*-#
import re

pattern1 = re.compile(r'^.*《.*》.{20,}$')

match =pattern1.match("电子版：《全球及中国单克隆抗体市场现状调查及未来发展趋势预测报告（2017-2022年）》pdf电子版下载")

if match:
    print match.group()
else:
    print 1


pattern2=re.compile(r'^.*报告.{20,}$')

match2=pattern2.match("2016-2021年中国单克隆抗体行业研究分析及发展趋势预测报告")

if match2:
    print match2.group()
else:
    print 2

pattern3=re.compile(r'^.*发展趋势.{20,}$')

match3=pattern3.match("济研：2012-2016年7月非肥料用氯化铵进出口贸易总额及发展趋势")

if match3:
    print match3.group()
else:
    print 3


slist=['2015年全球抗肿瘤药物已达789亿美元，总体市场占有率为8.27%']

str='2015年全球抗肿瘤药物已达789亿美元，总体市场占有率为8.27%'

print (str in slist)