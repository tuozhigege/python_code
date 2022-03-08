import re
import urllib.request
import xlwt
import sqlite3
from bs4 import BeautifulSoup

# 影片详情规则
findlink = re.compile(r'<a href="(.*?)">')
# 图片链接规则
findimg = re.compile(r'<img.*src="(.*?)"', re.S)  # re.s忽略换行符
# 标题规则
findtitle = re.compile(r'<span class="title">(.*?)</span>')
# 影片评分
findrat = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
# 概况
findinq = re.compile(r'<span class="inq">(.*)</span>')
# 相关内容
findbd = re.compile(r'<di<p class="">v class="bd">(.*?)</p>', re.S)

def main():
    baseurl = "https://movie.douban.com/top250?start="
    datelist = getdate(baseurl)
    savepath = "豆瓣电影top250.xls"
    savedate(savepath, datelist)

# 访问网页
def askurl(url):
    head = {   # 模拟头部信息
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 98.0.4758.102Safari / 537.36"
    }
    request = urllib.request.Request(url, headers=head)
    response = urllib.request.urlopen(request)
    html = response.read().decode("utf-8")
    return html

# 爬取网页
def getdate(baseurl):
    print('load...')
    list=[]
    for i in range(10):
        # 访问
        url = baseurl + str(i*25)
        html = askurl(url)
        print(f'正在爬取第{i+1}页', html)

        # 逐一解析
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_='item'):
            date = []
            item = str(item)
            title = re.findall(findtitle, item)  # 标题
            if len(title) > 1:
                date.append(title[0])
                otitle = title[1].replace('/', '').strip()
                date.append(otitle)
            else:
                date.append(title[0])
                date.append(" ")
            img = re.findall(findimg, item)[0]     # 图片链接
            date.append(img)
            rat = re.findall(findrat, item)[0]   # 评分
            date.append(rat)
            inq = re.findall(findinq, item)  # 概况
            if len(inq) == 0:
                date.append(" ")
            else:
                date.append(inq[0])
            link = re.findall(findlink, item)[0]  # 影片详情链接
            date.append(link)
            print(date)

            list.append(date) #添加到列表
    print(list)

    return list

# 保存数据
def savedate(path, list):
    print("save...")
    xls = xlwt.Workbook(encoding="utf-8")
    sheet = xls.add_sheet('sheet1')
    col = ("电影中文名", "外文名", "图片链接", "评分", "概况", "影片详情链接")
    for i in range(6):
        sheet.write(0, i, col[i])

    for i in range(len(list)):
        print("第%d条" % (i+1))
        date = list[i]
        for j in range(6):
            sheet.write(i+1, j, date[j])

    xls.save(path)
    print('success!')

if __name__ == "__main__":
    main()
