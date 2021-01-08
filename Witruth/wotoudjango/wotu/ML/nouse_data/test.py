#-*-coding:utf-8-*-#
import re

strs='是对方是对方是对方多少奋斗史当时发生的发对方舒服是对方是的啊是对方当发生的发 原文出处 sdf sd fsdf dsfasdf sdf'
pattern=re.compile(r'原文出处1')
match = pattern.search(strs)
if match:
    print(1)
else:
    print(2)
