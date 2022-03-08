import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


'''
    测试过，付费的下不了，就写着玩玩
'''

# https://dushu.baidu.com/pc/detail?gid=4306063500
# https://dushu.baidu.com/api/pc/getCatalog?data={%22book_id%22:%224306063500%22}
# https://dushu.baidu.com/api/pc/getChapterContent?data={%22book_id%22:%224306063500%22,%22cid%22:%224306063500|1569782244%22,%22need_bookinfo%22:1}

# "4306063500"
title = []
cid = []
book_id = "4306063500"

def getCatalog():       # 获取每个章节的名称和cid
    head = {"User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 98.0.4758.102Safari / 537.36"}
    url = "https://dushu.baidu.com/api/pc/getCatalog?data={%22book_id%22:%22" + book_id + "%22}"
    res = requests.get(url,headers=head)
    dic = res.json()
    items = dic['data']['novel']['items']
    for item in items:
        title.append(item['title'])
        cid.append(item['cid'])

def getChapterContent(c_id,tit,i):        # 获取章节内容并保存
    head = {"User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 98.0.4758.102Safari / 537.36"}
    url = "https://dushu.baidu.com/api/pc/getChapterContent?data={%22book_id%22:%22" + book_id + "%22,%22cid%22:%22" + book_id + "|" + c_id + "%22,%22need_bookinfo%22:1}"
    res = requests.get(url,headers=head)
    dic = res.json()
    content = dic['data']['novel']['content']
    content = tit + '\n\n' + content
    with open('./xs/' + str(i+1) + tit + '.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    jdt.update()
    # print(tit + 'OK！')

def main():     # 主函数
    getCatalog()
    global jdt
    jdt = tqdm(total=len(title))
    with ThreadPoolExecutor(20) as t:
        for i in range(len(title)):
            t.submit(getChapterContent, c_id=cid[i], tit=title[i], i=i)

def zh():       # 分章节下载完成后进行整合
    for i in range(len(title)):
        with open('./xs/' + str(i+1) + title[i] + '.txt', 'r', encoding='utf-8') as f1:
            with open('小说.txt', 'a', encoding='utf-8') as f2:
                f2.write(f1.read())
    print('ok')

def download():    # 单线程测试函数
    getCatalog()
    for i in range(len(title)):
        getChapterContent(cid[i], title[i], i)


if __name__=='__main__':
    main()
    zh()



