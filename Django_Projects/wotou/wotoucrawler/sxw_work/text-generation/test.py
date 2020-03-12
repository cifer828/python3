import requests

import sys
import lxml.html

import urllib
import matplotlib.pyplot as plt
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}


url = 'http://www.baidu.com/s?'
base_url='http://www.baidu.com'

decisionNode = dict(boxstyle="sawtooth", fc="0.8")
leafNode = dict(boxstyle="round4", fc="0.8")
arrow_args = dict(arrowstyle="<-")
#这是递归计算树的叶子节点个数，比较简单
def getNumLeafs(myTree):
	numLeafs = 0
	firstStr = list(myTree.keys())[0]
	secondDict = myTree[firstStr]
	for key in secondDict.keys():
		if type(secondDict[key]).__name__=='dict':#test to see if the nodes are dictonaires, if not they are leaf nodes
			numLeafs += getNumLeafs(secondDict[key])
		else:   numLeafs +=1
	return numLeafs
#这是递归计算树的深度，比较简单
def getTreeDepth(myTree):
	maxDepth = 0
	firstStr = list(myTree.keys())[0]
	secondDict = myTree[firstStr]
	for key in secondDict.keys():
		if type(secondDict[key]).__name__=='dict':#test to see if the nodes are dictonaires, if not they are leaf nodes
			thisDepth = 1 + getTreeDepth(secondDict[key])
		else:   thisDepth = 1
		if thisDepth > maxDepth: maxDepth = thisDepth
	return maxDepth
#这个是用来一注释形式绘制节点和箭头线，可以不用管
def plotNode(nodeTxt, centerPt, parentPt, nodeType):
	createPlot.ax1.annotate(nodeTxt, xy=parentPt,  xycoords='axes fraction',
			 xytext=centerPt, textcoords='axes fraction',
			 va="center", ha="center", bbox=nodeType, arrowprops=arrow_args )
#这个是用来绘制线上的标注，简单
def plotMidText(cntrPt, parentPt, txtString):
	xMid = (parentPt[0]-cntrPt[0])/2.0 + cntrPt[0]
	yMid = (parentPt[1]-cntrPt[1])/2.0 + cntrPt[1]
	createPlot.ax1.text(xMid, yMid, txtString, va="center", ha="center", rotation=30)
#重点，递归，决定整个树图的绘制，难（自己认为）
def plotTree(myTree, parentPt, nodeTxt):#if the first key tells you what feat was split on
	numLeafs = getNumLeafs(myTree)  #this determines the x width of this tree
	depth = getTreeDepth(myTree)
	firstStr =list(myTree.keys())[0]	 #the text label for this node should be this
	cntrPt = (plotTree.xOff + (1.0 + float(numLeafs))/2.0/plotTree.totalW, plotTree.yOff)
	plotMidText(cntrPt, parentPt, nodeTxt)
	plotNode(firstStr, cntrPt, parentPt, decisionNode)
	secondDict = myTree[firstStr]
	plotTree.yOff = plotTree.yOff - 1.0/plotTree.totalD
	for key in secondDict.keys():
		if type(secondDict[key]).__name__=='dict':#test to see if the nodes are dictonaires, if not they are leaf nodes
			plotTree(secondDict[key],cntrPt,str(key))		#recursion
		else:   #it's a leaf node print the leaf node
			plotTree.xOff = plotTree.xOff + 1.0/plotTree.totalW
			plotNode(secondDict[key], (plotTree.xOff, plotTree.yOff), cntrPt, leafNode)
			plotMidText((plotTree.xOff, plotTree.yOff), cntrPt, str(key))
	plotTree.yOff = plotTree.yOff + 1.0/plotTree.totalD
#if you do get a dictonary you know it's a tree, and the first element will be another dict
#这个是真正的绘制，上边是逻辑的绘制
def createPlot(inTree):
	fig = plt.figure(1, facecolor='white')
	fig.clf()
	axprops = dict(xticks=[], yticks=[])
	createPlot.ax1 = plt.subplot(111, frameon=False)	#no ticks
	plotTree.totalW = float(getNumLeafs(inTree))
	plotTree.totalD = float(getTreeDepth(inTree))
	plotTree.xOff = -0.5/plotTree.totalW; plotTree.yOff = 1.0;
	plotTree(inTree, (0.5,1.0), '')
	plt.show()

def search(payload):

    r = requests.get(url+urllib.parse.urlencode(payload), headers=headers, timeout=5)
    print (r.url)
    print (r.status_code)
    #print (r.content)

    map_dict=dict()


    dom = lxml.html.document_fromstring(r.content)
    if len(dom.xpath('//div[@class="opr-recommends-merge-content"]'))>0:
        table=dom.xpath('//div[@class="opr-recommends-merge-content"]')[0]
        div_len=len(table.xpath('./div'))
        print (div_len)
        for i in range(1,div_len+1,2):
            #index=0
            type=table.xpath('./div['+str(i)+']/span')[0].text
            #print (type)
            map_dict[type]=[]
            first_low=len(table.xpath('./div['+str(i+1)+']/div[1]/div'))
            for j in range(1,first_low+1):
                #url1=table.xpath('./div['+str(i+1)+']/div[1]/div['+str(j)+']/div[2]/a')[0].get('href')[3:]
                #print (url1)
                text1=table.xpath('./div['+str(i+1)+']/div[1]/div['+str(j)+']/div[2]/a')[0].text
                #print (text1)1
                map_dict[type].append(text1)

            if len(table.xpath('./div['+str(i+1)+']/textarea'))>0:
                show_up=table.xpath('./div['+str(i+1)+']/textarea')[0].value
                sub_dom = lxml.html.document_fromstring(show_up.strip())
                domdiv=sub_dom.xpath('//div[@class="opr-recommends-merge-morelists"]')[0]
                row_len=len(domdiv.xpath('./div'))
                #print (row_len)
                for t in range(1,row_len+1):
                    col_len=len(domdiv.xpath('./div['+str(t)+']/div'))
                    #print (col_len)
                    for s in range(1,col_len):
                        #print (len(domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div')))
                        #url1=domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div[2]/a')[0].get('href')[3:]
                        text1=domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div[2]/a')[0].text
                        #print (url1)
                        #print (text1)
                        map_dict[type].append(text1)
        return map_dict



first_word=u'生物医药'
payload = {'wd': first_word}
word_dict=dict()

word_dict[first_word]=search(payload)

for key,value in word_dict[first_word].items():
    for i in range(len(value)):
        payload={'wd':value[i]}
        word_dict[value[i]]=search(payload)

        # for key1,value1 in word_dict[value[i]].items():
        #     for t in range(len(value1)):
        #         payload={'wd':value1[t]}
        #         word_dict[value1[t]]=search(payload)
#createPlot(word_dict)
print (word_dict)

jsObj = json.dumps(word_dict,ensure_ascii=False)

fileObject = open('jsonFile.json', 'w')
fileObject.write(jsObj)
fileObject.close()





