'''
Author       : UniMars
Date         : 2020-11-03 11:06:43
LastEditors  : UniMars
LastEditTime : 2020-11-03 19:55:32
Description  : file head
'''
from bs4.element import Tag
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(r'E:/Programs/Code/python')
import myPackage.myIO
import re

'''
Description: 匹配正则表达式
param {str} str
param {str} re
return {*}
'''
def matchStr(str:str,re:str)->str:
    if(re.compile(re, str) != None):
        return re.compile(re, str).match
    else:
        return None

'''
Description: 爬取网页对象
param {str} doc_url
return {Response}
'''
def get_doc(doc_url:str):
    url=doc_url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}  #给请求指定一个请求头来模拟chrome浏览器
    r = requests.get(url,headers=headers)
    return r
'''
Description: 获取body
param {BeautifulSoup} doc
return {Tag}
'''
def get_body(doc:BeautifulSoup)->Tag:
    body=doc.find(class_="body")
    return body


'''
爬取的是html文本

编码？

首先获取目录 正文 or 直接获取正文自动生成目录？

igored

标题
连接
脚注
片段
代码
表格

遍历读取节点
判断类型
'''

'''
Description: 将body Tag 转换为markdown文本
param {Tag} tag
param {str} path
param {str} motherpath
return {None}
'''
def output(tag:Tag,path:str,motherTag=None)->None:
    #保存母节点
    if motherTag==None:
        motherTag =tag
        pass

#检索节点类型
#是否为body节点
    if tag['class']=="body":
        for child in tag.children:
            output(child,path,motherTag)
        pass
    #是否为分区
    elif tag['class']=="section":
        myPackage.myIO.my_write(path,"\n\n")
        for child in tag.children:
            output(child, path,motherTag)
        pass
    #是否为标题
    elif matchStr(tag.name, 'h[1-9]') != None:
        myPackage.myIO.my_write(path, "\n")
        num=(int)(matchStr(tag.name, 'h[1-9]')[-1])
        #输出‘#’
        for i in range(num):
            myPackage.myIO.my_write(path,"#")
        myPackage.myIO.my_write(path, " ")
        #遍历
        for child in tag.children:
            output(child, path,motherTag)
        for i in range(num):
            myPackage.myIO.my_write(path, "#")
        #换行
        myPackage.myIO.my_write(path, "\n")
        pass
    #是否为文本
    elif tag.name=='None':
        myPackage.myIO.my_write(path,tag.string)
        pass
    #是否为连接
    #?id问题?
    elif tag.name=='a':
        if tag['class']=="footnote-reference":
            myPackage.myIO.my_write(path, " ")
            myPackage.myIO.my_write(path=path, str="[^")
            myPackage.myIO.my_write(path, tag.string[1:-1])
            myPackage.myIO.my_write(path=path,str="]")
            pass
        if matchStr(tag['href'],'http')!=None:
            myPackage.myIO.my_write(path=path,str="[")
            myPackage.myIO.my_write(path=path,str=tag.string)
            myPackage.myIO.my_write(path=path,str="]")
            myPackage.myIO.my_write(path=path,str="(")
            myPackage.myIO.my_write(path=path,str=tag['href'])
            myPackage.myIO.my_write(path=path,str=")")
        elif matchStr(tag['href'], '#')!=None:
            #TODO
            pass
        pass
    #是否为无序列表
    elif tag.name=='ul':
        for li in tag.children:
            myPackage.myIO.my_write(path=path, str="- ")
            output(li, path, motherTag)
            myPackage.myIO.my_write(path=path, str="\n")
            pass
        pass
    #是否为有序列表
    elif tag.name=='ol':
        n=1
        for li in tag.children:
            myPackage.myIO.my_write(path=path, str=(str)(n)+". ")
            output(li, path, motherTag)
            myPackage.myIO.my_write(path=path, str="\n")
            n+=1
            pass
        pass
    #是否为代码块
    elif tag['class']=="highlight":
        myPackage.myIO.my_write(path=path, str="```python\n")
        for child in tag.children:
            output(child, path, motherTag)
        myPackage.myIO.my_write(path=path,str="```\n")
        pass
    #是否为代码
    elif tag.name=="code":
        myPackage.myIO.my_write(path=path, str="`")
        for child in tag.children:
            output(child, path, motherTag)
        myPackage.myIO.my_write(path=path,str="`")
        pass
    #是否为表格
    elif tag.name=="table":
        #判断表头
        if tag.name=="thead":
            myPackage.myIO.my_write(path=path,str="\n|")
            for th in tag.tr.children:
                if th.name=="th":
                    #判断单元
                    n=0
                    output(th.string,path,motherTag)
                    myPackage.myIO.my_write(path=path,str="|")
                    n+=1
                    pass
                pass
            myPackage.myIO.my_write(path=path, str="\n|")
            #表头换行格式
            for i in range(n):
                myPackage.myIO.my_write(path=path,str="---|")
                pass
            pass
        #判断表格主体
        elif tag.name=="tbody":
            myPackage.myIO.my_write(path=path, str="\n|")
            for td in tag.tr.children :
                if td.name=="td":
                    output(td.string,path,motherTag)
                    myPackage.myIO.my_write(path=path,str="|")
                    pass
                pass
            pass
        #TODO tfoot        
        #TODO 列
        myPackage.myIO.my_write(path=path,str="\n")
        pass

    #是否为换行
    elif tag.name=="br":
        myPackage.myIO.my_write(path=path,str="\n")
        pass

    elif tag.name=="b" or tag.name=="strong":
        myPackage.myIO.my_write(path=path,str="**")
        myPackage.myIO.my_write(path=path,str=tag.string)
        myPackage.myIO.my_write(path=path,str="**")
        pass
    
    elif tag.name=="em":
        myPackage.myIO.my_write(path=path,str="_**")
        myPackage.myIO.my_write(path=path,str=tag.string)
        myPackage.myIO.my_write(path=path,str="**_")
        pass

    elif tag.name=="i":
        myPackage.myIO.my_write(path=path,str="_")
        myPackage.myIO.my_write(path=path,str=tag.string)
        myPackage.myIO.my_write(path=path,str="_")
        pass

    elif tag.name=="del":
        myPackage.myIO.my_write(path=path,str="~~")
        myPackage.myIO.my_write(path=path,str=tag.string)
        myPackage.myIO.my_write(path=path,str="~~")
        pass

    elif tag.name=="sub":
        myPackage.myIO.my_write(path=path,str="^")
        myPackage.myIO.my_write(path=path,str=tag.string)
        myPackage.myIO.my_write(path=path,str="^")
        pass

    elif tag.name=="sup":
        myPackage.myIO.my_write(path=path,str="~")
        myPackage.myIO.my_write(path=path,str=tag.string)
        myPackage.myIO.my_write(path=path,str="~")
        pass

    




    pass
