# -*- codeing = utf-8 -*-
# @Author : tuozhigege


import requests
from lxml import etree
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
import time

'''

    1.单线程获取当前页每一章图片的详情页链接
    2.单线程获取一章图片尾页，并获取每页图片
    3.单线程保存图片
    4.获取当前类别每页链接，然后和1.串起来
    5.多线程运行步骤2，速度提升，但还是有点慢，且步骤1耗时较长
    6.采取异步协程方法运行步骤1，速度明显提升，从21秒变为2秒！
    7.复制出去，全程采用异步，初测发现，只下载10个图集时，多线程10线程耗时112秒，异步76秒.下载100个图集时多线程耗时151秒，测试异步时网站崩了，但结果可想而知，要慢很多！
        但此时的异步只是在download_jpg函数采取异步，download函数只能用单线程调用，不知道可不可以多线程中嵌套异步，但在测试中程序运行几秒就停止了，可能还是操作不到位
    8.我将download_jpg函数写入main函数中进行异步调用，产生一种异步嵌套异步的效果，下载10图集仅用27秒.但只要图集一多程序就崩，还是多线程下靠谱！！

'''

charturl = []
# charturl = ['https://www.umeitu.com//meinvtupian/siwameinv/27174.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27175.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27176.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27177.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27178.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27179.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27180.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27181.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/20928.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/20938.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27182.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27183.htm', 'https://www.umeitu.com//meinvtupian/siwameinv/27184.htm']

baseurl = 'https://www.umeitu.com/'
re_totalpage = re.compile('下一页</a>.*;<a href="(.*?).htm">尾页</a>')



# 参数：图片页地址，保存路径。从图片页地址获取到图片的下载地址，并保存到path路径下
def download_jpg(jqg_pageurl,path):
    resq = requests.get(jqg_pageurl)
    resq.encoding = "utf-8"
    tree = etree.HTML(resq.text)
    jqg_url = tree.xpath('//p//img/@src')[0]
    jpg = requests.get(jqg_url)
    with open(path, 'wb') as f:
        f.write(jpg.content)


# 主下载函数,从全局变量charturl取出章节地址，获得章节内每张图片的图片页地址，并传入download_jpg下载每页图片
def download(i):
    url = charturl[i]
    res = requests.get(url)
    res.encoding = 'utf-8'
    totalpage_temp = re.findall(re_totalpage, res.text)[0]
    totalpage = totalpage_temp.split('_')[-1]
    mid_url = totalpage_temp.split('_')[0]
    for j in range(int(totalpage)):
        if j == 0:
            page = ''
        else:
            page = '_' + str(j + 1)
        jqg_pageurl = baseurl + mid_url + page + '.htm'
        path = f'/下载/picture/{i}_{j}.jpg'
        download_jpg(jqg_pageurl, path)
    jdt.update()


# 获取每页章节链接并加入全局变量
async def getcharturl(url):
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as res:
            res.encoding = "utf-8"
            tree = etree.HTML(await res.text())
            hurl = tree.xpath('/html/body/div[2]/div[8]/ul/li/a/@href')
            for u in hurl:
                charturl.append(url.split("/meinvtupian")[0] + u)

# 获取总页数，拼接每页链接，然后异步调用getcharturl获取每章链接
async def getpageurl():
    res = requests.get(g_url)
    res.encoding = 'utf-8'
    totalpage_ = re.findall(re_totalpage, res.text)[0]
    totalpage = totalpage_.split('_')[-1]
    tasks = []
    for i in range(int(totalpage)):
        if i == 0:
            page = ''
        else:
            page = '_' + str(i + 1)
        pageurl = baseurl + totalpage_.split('_')[0] + page + '.htm'
        task = asyncio.create_task(getcharturl(pageurl))
        tasks.append(task)
    await asyncio.wait(tasks)


if __name__ == '__main__':
    # 获取详情链接
    # g_url = "https://www.umeitu.com/meinvtupian/xingganmeinv/index.htm"
    g_url = "https://www.umeitu.com/meinvtupian/siwameinv/"
    # g_url = 'https://www.umeitu.com/meinvtupian/rentiyishu/index.htm'

    loop = asyncio.get_event_loop()

    star = time.time()
    # 异步获取所有页所有图集链接
    loop.run_until_complete(getpageurl())
    chart_num = len(charturl)
    end = time.time()

    print(f'共{chart_num}个图集，开始下载！', end-star)

    jdt = tqdm(total=chart_num)     # 显示进度条

    # 多线程下载图集，100线程池
    star = time.time()
    with ThreadPoolExecutor(100) as pool:
        for i in range(chart_num):
            pool.submit(download, i=i)
    end = time.time()
    print(end - star)   # 10线程下10图集112秒,100线程100图集151秒
