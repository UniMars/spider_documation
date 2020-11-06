'''
Author       : UniMars
Date         : 2020-11-03 11:06:43
LastEditors  : UniMars
LastEditTime : 2020-11-06 15:07:31
Description  : file head
'''
import sys

import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

sys.path.append(r'E:/Programs/Code/python')
import re
import time

import myPackage.myIO

'''
Description: 爬取网页对象
param {str} doc_url
return {Response}
'''


def get_doc(doc_url: str):
    time_start=time.time()
    url = doc_url
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
    }  #给请求指定一个请求头来模拟chrome浏览器
    r = requests.get(url, headers=headers)
    print("--------------------------------\nhtml got")
    time_end = time.time()
    print("total time=%.2f s"%(time_end-time_start))
    return r

'''
Description: 将body Tag 转换为markdown文本
param {Tag} tag
param {str} path
param {str} motherpath
return {None}
'''


def output(tag: Tag, path: str) -> None:

    #检索Tag类型
    #是否为文本
    # and tag.name==None
    if isinstance(tag, NavigableString):
        #TODO 特殊字符处理
        text=""+tag.string
        pattern = r'(?<=[^`])(<\S+?>)'
        while(re.search(pattern,text)!=None):
            text=re.sub(pattern,r'`\1`',text)
        myPackage.myIO.my_write(path,text)
        return

    else:
        #id问题
        if tag.get('id') != None:
            myPackage.myIO.my_write(path, text="<div id=\"")
            myPackage.myIO.my_write(path=path, text=tag['id'])
            myPackage.myIO.my_write(path, text="\"></div>\n")
            pass

        #检索节点类型
        isClass = tag.get('class') != None
        #是否为body节点
        if isClass and "body" in tag.get('class'):
            start_time=time.time()
            myPackage.myIO.my_write(path,text="",mode='w+')
            for child in tag.children:
                output(child, path)
                pass
            #生成目录
            toc = "\n"
            with open(path, 'r') as f:
                for line in f:
                    if re.match('#+', line):
                        num = len(re.match('#+', line).group()) - 1
                        for i in range(num):
                            toc = toc + "\t"
                            pass
                        str_head = line[num + 1:].rstrip().lstrip()
                        #去除空格与符号
                        lst_head=str_head.split()
                        for char in lst_head:
                            reg = re.compile(r"[a-zA-Z0-9\u2E80-\u9FFF]")
                            if not re.match(reg, char):
                                lst_head.remove(char)
                            pass
                        #连接字符串
                        str_link="#"+"-".join(lst_head)
                        toc = toc + "- [" + str_head + "]("+str_link+")\n"
                        pass
                    pass
                pass
            #写入目录
            myPackage.myIO.my_write(path=path, text=toc,mode='r+')
            end_time=time.time()
            during=end_time-start_time   
            t=[0,0,0]
            n=0
            while(n<3):
                t[n]=during%60
                during=int(during/60)
                n=n+1
            print("process time :%dh%min%ss"%(t[2],t[1],t[0]))
            return

        #是否为分区
        elif isClass and "section" in tag.get('class'):
            myPackage.myIO.my_write(path, "\n\n")
            for child in tag.children:
                output(child, path)
            pass

        #是否为代码块
        elif  isClass and "highlight" in tag.get('class'):
            myPackage.myIO.my_write(path=path,text="```python\n")
            for code in tag.strings:
                myPackage.myIO.my_write(path=path,text=code)
            myPackage.myIO.my_write(path=path,text="```\n")
            pass

        #是否为标题
        elif re.match('h[1-9]', tag.name) != None:
            # myPackage.myIO.my_write(path, "\n",)
            num = (int)((re.match('h[1-9]', tag.name).group())[1:])
            #输出‘#’
            for i in range(num):
                myPackage.myIO.my_write(path, "#")
            myPackage.myIO.my_write(path, " ")
            #遍历
            for child in tag.children:
                output(child, path)
            pass

        #是否为连接
        elif tag.name == 'a':
            myPackage.myIO.my_write(path=path,text="[")
            for child in tag.children:
                output(child, path)
            myPackage.myIO.my_write(path=path,text="]")
            myPackage.myIO.my_write(path=path,text="(")
            myPackage.myIO.my_write(path=path,text=tag.get('href'))
            myPackage.myIO.my_write(path=path,text=")")
            pass

        #是否为无序列表
        elif tag.name == 'ul':
            for li in tag.children:
                if li.name=="li":
                    myPackage.myIO.my_write(path=path,text="- ")
                    for child in li.children:
                        output(child, path)
                    myPackage.myIO.my_write(path=path,text="\n")
                    pass
                pass
            pass

        #是否为有序列表
        elif tag.name == 'ol':
            n = 1
            for li in tag.children:
                if li.name=="li":
                    myPackage.myIO.my_write(path=path,text=(str)(n) + ". ")
                    for child in li.children:
                        output(child, path)
                    myPackage.myIO.my_write(path=path,text="\n")
                    n += 1
                    pass
                pass
            pass


        #是否为代码
        elif tag.name == "code":
            myPackage.myIO.my_write(path=path,text="`")
            for child in tag.children:
                output(child, path)
            myPackage.myIO.my_write(path=path,text="`")
            pass

        #是否为表格
        elif tag.name == "table":
            if (tag('frame') == "void" and tag('rules') == "none"):
                for tr in tag.descendants:
                    if tr.name == "tr":
                        for td in tr.children:
                            if td.name=="td":
                                for child in td.children:
                                    output(child, path)
                                    pass
                                pass
                            myPackage.myIO.my_write(path=path,text=" ")
                            pass
                        myPackage.myIO.my_write(path=path,text="\n")
                        pass
                    pass
                pass

            else:
                for part in tag:
                    #判断表头
                    if part.name == "thead":                        
                        for string in part.strings:
                            pattern=r'\n'
                            while(re.search(pattern,string)!=None):
                                string=re.sub(pattern,r'',string)
                            pass
                        myPackage.myIO.my_write(path=path,text="\n|")
                        n = 0
                        for th in tag.tr.children:
                            if th.name == "th":
                                #判断单元
                                for child in th.children:
                                    output(child, path)
                                myPackage.myIO.my_write(path=path,text="|")
                                n += 1
                                pass
                            pass
                        myPackage.myIO.my_write(path=path,text="\n|")
                        #表头换行格式
                        for i in range(n):
                            myPackage.myIO.my_write(path=path,text="---|")
                            pass
                        myPackage.myIO.my_write(path=path,text="\n")
                        pass
                    #判断表格主体
                    elif part.name == "tbody":
                        for string in part.strings:
                            pattern=r'\n'
                            while(re.search(pattern,string)!=None):
                                string=re.sub(pattern,r'',string)
                            pass
                        for tr in part.children:
                            if tr.name=="tr":
                                myPackage.myIO.my_write(path=path,text="|")
                                for td in tr.children:
                                    if td.name == "td":
                                        for child in td.children:
                                            output(child, path)
                                        myPackage.myIO.my_write(path=path,text="|")
                                        pass
                                    pass
                                myPackage.myIO.my_write(path=path, text="\n")
                                pass
                            pass
                        pass
                    #TODO tfoot
                    #TODO 列
                    pass
                pass
            pass


        #是否为换行
        elif tag.name == "br":
            myPackage.myIO.my_write(path=path,text="\n")
            pass

        #是否为加粗
        elif tag.name == "b" or tag.name == "strong":
            myPackage.myIO.my_write(path=path,text="**")
            for child in tag.children:
                output(child, path)
            myPackage.myIO.my_write(path=path,text="**")
            pass

        #是否为强调
        elif tag.name == "em":
            myPackage.myIO.my_write(path=path,text="___")
            for child in tag.children:
                output(child, path)
            myPackage.myIO.my_write(path=path,text="___")
            pass
        #是否为斜体
        elif tag.name == "i":
            myPackage.myIO.my_write(path=path,text="_")
            for child in tag.children:
                output(child, path)
            myPackage.myIO.my_write(path=path,text="_")
            pass
        #是否地址
        elif tag.name == "address":
            myPackage.myIO.my_write(path=path,text="_")
            for child in tag.children:
                output(child, path)
            myPackage.myIO.my_write(path=path,text="_\n")
            pass
        #是否为删除线
        elif tag.name == "del":
            myPackage.myIO.my_write(path=path,text="~~")
            for child in tag.children:
                output(child, path)
            myPackage.myIO.my_write(path=path,text="~~")
            pass
        #是否为上标
        elif tag.name == "sub":
            myPackage.myIO.my_write(path=path,text="^")
            myPackage.myIO.my_write(path=path,text=tag.string)
            myPackage.myIO.my_write(path=path,text="^")
            pass
        #是否为下标
        elif tag.name == "sup":
            myPackage.myIO.my_write(path=path,text="~")
            myPackage.myIO.my_write(path=path,text=tag.string)
            myPackage.myIO.my_write(path=path,text="~")
            pass
        #是否为引用
        elif tag.name == "blockquote":
            myPackage.myIO.my_write(path=path,text=">")
            for child in tag.children:
                output(child, path)
            myPackage.myIO.my_write(path=path,text="\n")
            pass
        #是否为短引用
        elif tag.name == "q":
            if tag.get('cite') != None:
                myPackage.myIO.my_write(path=path,text="[\"")
                for child in tag.children:
                    output(child, path)
                myPackage.myIO.my_write(path=path,text="\"] (")
                myPackage.myIO.my_write(path=path,text=tag.get('cite'))
                myPackage.myIO.my_write(path=path,text=")")
            else:
                myPackage.myIO.my_write(path=path,text="\"")
                for child in tag.children:
                    output(child, path)
                myPackage.myIO.my_write(path=path,text="\"")
                pass
            pass
        #TODO img
        else:
            for child in tag.children:
                output(child, path)
                pass
        pass
    pass


'''
#TODO
'''

if __name__ == "__main__":
    str = "https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/"
    html = get_doc(str).text
    soup=BeautifulSoup(html,'lxml')
    body=soup.find(class_="body")
    path="E:/Programs/Code/python/projects/spider_documation/test/"+"test.md"
    output(body,path)
    pass
