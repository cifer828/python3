# -*- coding:utf8 -*-
import urllib

if __name__ == '__main__':
    url_get_base = "http://api.ltp-cloud.com/analysis/"
    args = {
        'api_key' : '81Z1d8x5v1ueUztElkOH9khMTHhvKLYMRwXQUGih',
        'text' : '2017年5月19日讯 /生物谷BIOON/ --德国制药巨头拜耳（Bayer）近日宣布，美国FDA已授予抗癌药copanlisib新药申请（NDA）优先审查资格，该NDA寻求批准copanlisib作为一种单药疗法，用于既往已接受至少2次治疗的复发性或难治性滤泡性淋巴瘤（FL）患者。优先审查（PR）是FDA的一个新药审查通道，旨在加速开发及审查治疗严重的或危及生命的疾病的新药，保障在最短时间内为患者提供新的治疗选择。根据处方药用户收费法（PDUFA），获得优先审查资格（PRD）的药物，FDA将给予加速审查并在6个月完成审查，而不是标准的10个月。如果获批上市，copanlisib将与吉利德的首创新药——口服PI3K抑制剂Zydelig（idelalisib）展开竞争，这是FDA批准的全球首个PI3K抑制剂，已获批用于3种B细胞肿瘤的治疗，分别为：（1）批准Zydelig联合罗氏（Roche）抗癌药美罗华（Rituxan，通用名：rituximab，利妥昔单抗），用于适合Rituxan单药疗法的复发性慢性淋巴细胞白血病（CLL）患者的治疗；（2）批准Zydelig作为单药疗法，用于既往接受过至少2种系统治疗方案的复发性滤泡B细胞非霍奇金淋巴瘤（FL）患者和小细胞淋巴瘤（SLL）患者的治疗。copanlisib是一种新颖的静脉注射型泛I类磷脂酰肌醇-3-激酶（PI3K）抑制剂，针对PI3K-α和PI3K-δ异构体具有主要的抑制活性。PI3K信号通路参与细胞的生长、存活和新陈代谢，该通路的失调在非霍奇金淋巴瘤（NHL）中发挥了重要作用。copanlisib通过静脉输注给药，给药模式为：治疗3周（每周一次，每次1小时）后停药1周。在I期和II期临床研究中，copanlisib针对复发性惰性和侵袭性非霍奇金淋巴瘤（NHL）表现出强大的临床疗效。目前，拜耳正在推进一个大型临床开发项目，其中包括在既往已接受治疗的复发性或难治性惰性NHL患者中开展的III期临床研究。非霍奇金淋巴瘤（NHL）是最常见的血液系统恶性肿瘤，是第十大最常见癌症类型，由一组高度异质性的疾病组成，根据肿瘤细胞增殖速度和临床特点，可分为侵袭性NHL和惰性NHL。其中，滤泡性淋巴瘤（FL）是惰性NHL最常见的组织学亚型。之前，FDA已授予copanlisib用于该适应症的快速通道地位和孤儿药地位。此外，FDA也已授予copanlisib治疗脾脏、淋巴结、淋巴结外边缘区淋巴瘤（MZL）的孤儿药地位。copanlisib NDA的提交，是基于II期临床研究CHRONOS-1的数据。该研究是一项开放标签、单组研究，在既往接受过至少2次治疗的复发性或难治性惰性非霍奇金淋巴瘤（iNHL，包括滤泡淋巴瘤[FL]）患者中开展。全分析集纳入了142例患者，其中141例为iNHL患者。数据分析时，中位治疗持续时间为22周，46%患者仍在接受治疗。横跨全部患者组的数据显示，客观缓解率（ORR）为59.2%，其中完全缓解率（CR）为12%；中位缓解持续时间（DOR）超过98周（687天）。在滤泡性淋巴瘤（FL）亚组（n=104）中，copanlisib单药治疗取得的总缓解率（ORR）为58.7%，其中完全缓解率（CR）为14.4%，中位缓解持续时间（DOR）为52周（370天）。该研究中，copanlisib的安全性与以往公布的数据一致。最常见的治疗相关不良事件为短暂的高血糖（所有级别：49%；≥3级：40%；＞4级：未发生）和高血压（所有级别：29%；≥3级：23%；＞3级：未发生）',
        'pattern' : 'ws',
        'format' : 'plain'
    }
    result = urllib.urlopen(url_get_base, urllib.urlencode(args)) # POST method
    content = result.read().strip()
    print(content)
