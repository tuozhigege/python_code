# -*- codeing = utf-8 -*-
# @Author : tuozhi

import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import os
from lxml import etree    # xpath方式解析数据
from bs4 import BeautifulSoup


path_q = "D:/下载/小说"
baseurl = "https://www.bqkan8.com"   # 用于拼接章节url
zurl = []   # 储存每一章节地址
title = []    # 储存每一章节标题
tit = ['']  # 小说名


'''
函数作用：获取所有章节名以及章节链接地址，存入全局变量中
参数：无
返回：无
'''

def geturl(url):
    # url = "https://www.bqkan8.com/1_1094/"
    head = {"User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 98.0.4758.102Safari / 537.36"}
    req = requests.get(url, headers=head)
    req.encoding = "gbk"
    bf = BeautifulSoup(req.text, features="lxml")
    tit[0] = bf.find_all('meta', property="og:title")[0].get('content')
    bf = bf.find_all('div', class_='listmain')[0]
    bf_a = BeautifulSoup(str(bf), features="lxml")
    list = bf_a.find_all('a')[12:]
    for i in range(len(list)):
        title.append(list[i].text)
        zurl.append(baseurl + list[i].get('href'))


'''
函数作用：获取网页内容并进行解析，提取出正文部分
参数：url（str）:章节网页地址
返回：返回网页正文部分
'''
def getcontent(url):
    # url = "https://www.bqkan8.com/1_1094/5403177.html"
    head = {"User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 98.0.4758.102Safari / 537.36"}
    req = requests.get(url, headers=head)
    tree = etree.HTML(req.text)
    content = tree.xpath('//*[@id="content"]/text()')[:-2]
    for i in range(len(content)):
        content[i] = content[i]
    text = '\n\n'.join(content)
    return text

'''
函数作用：保存文本
参数：
    path(str):保存路径
    text(str):保存文本
返回：无
'''
def save(path,text):
    with open(path, 'a', encoding='utf-8') as f:
        f.write('\n')
        f.writelines(text)
        f.write('\n')


'''
函数作用：整合数据到一个文件中
参数：num
返回：无
'''
def zh(num):
    for i in range(num):
        with open(path_q + f"/hc/{i}.txt", 'rb') as f1:
            with open(path_q + f'/{tit[0]}.txt', 'ab') as f2:
                f2.write(f1.read())
        os.remove(path_q + f"/hc/{i}.txt")


'''
函数作用：线程工作
参数：i
返回：无
'''

def thread_job(i):
    text = getcontent(zurl[i])
    text = title[i] + "\n\n" + text
    path = path_q + f"/hc/{i}.txt"
    save(path, text)
    jdt.update()


if __name__ == '__main__':
    url = input("请输入www.bqkan8.com中你要下载的小说首页链接：")
    # threads = []
    geturl(url)
    chart_num = len(title)
    path = path_q + "/hc"
    try:
        os.mkdir(path=path)  # 创建文件夹
    except:
        pass

    if input(f'《{tit[0]}》共{chart_num}章，是否开始下载【y/n】?') == 'n':
        print('臣退了！')
        exit(666)

    print('开始多线程下载,请等待。。')

    jdt = tqdm(total=chart_num)  # 显示进度条

    with ThreadPoolExecutor(50) as pool:
        for i in range(chart_num):
            pool.submit(thread_job, i)

    zh(chart_num)  # 开始整合数据
    print(f'《{tit[0]}》下载成功！')











