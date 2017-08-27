# -*- coding:utf-8 -*-

import os
import time
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup

# 首页链接，也用来构成后面每个图集的链接
index_url = 'http://www.mmjpg.com/'
# 默认存储文件夹
album_dir = 'C:\\Users\\novia\\Documents\\IMG\\MMJPG\\'

session = requests.session()
s = session.post(index_url)


# 每次请求的 header 均不同，需要自己构造，以免被封
def get_heades(album_id, pic_id):
    headers = {
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Language': 'zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.6,en;q=0.4,ja;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'img.mmjpg.com',
        'Connection': 'Keep-Alive',
        'Referer': 'http://www.mmjpg.com/mm/' + str(album_id) + '/' + str(pic_id)
    }
    return headers


# 获取最大图集数量
def max_album(url):
    html = session.get(url).text
    bs_obj = BeautifulSoup(html, 'html.parser')
    maxalbum_url = bs_obj.find('div', {'class': 'pic'}).find('li').find('a').attrs['href']
    maxalbum = maxalbum_url.replace('http://www.mmjpg.com/mm/', '')
    return int(maxalbum)


# 获取每个图集最大图片数量和年份
def pic_info(url):
    html = session.get(url).text
    bs_obj = BeautifulSoup(html, 'html.parser')
    pages = bs_obj.find('div', {'class': 'page'}).find_all('a')
    page_list = []
    for page in pages:
        page_list.append(page.get_text())
    max_pic = int(page_list[-2])
    pic_url = bs_obj.find('div', {'class': 'content'}).find('img')['src']
    pic_year = pic_url.replace('http://img.mmjpg.com/', '')
    pic_year = pic_year[:4]
    return [max_pic, pic_year]


# 存储图片，不能用 urlretrieve 会显示盗链
def save_pic(pic_file, pic_to_dir):
    fo = open(pic_to_dir, 'wb')
    fo.write(pic_file)
    fo.close()


# 获取所有图集的图片并下载到对应文件夹
def get_album(start=1, end=max_album(index_url), timesleep=30):
    print('开始采集 MMJPG ...\n' + '-' * 50 + '\n')
    for i in range(start, end + 1):
        # 组成图集链接
        album_url = 'http://www.mmjpg.com/mm/' + str(i)
        # 图集标题
        album_name = BeautifulSoup(urlopen(album_url), 'html.parser').title.get_text().replace('_妹子图', '')
        # 图集存储的文件夹名称
        album_dir_name = album_dir + str(i) + ' ' + album_name
        # 如果图集的文件夹已经存在说明曾经抓取过，则跳过
        if os.path.exists(album_dir_name):
            print(str(i) + ' ' + album_name + ' 已抓取过\n')
            continue
        else:
            print('Processing: ' + str(i) + ' ' + album_name)
            # 建立图集文件夹
            os.makedirs(album_dir_name)
            # 抓取图集中的每一个图片
            for j in range(1, pic_info(album_url)[0] + 1):
                # 图片的链接地址
                pic_url = 'http://img.mmjpg.com/' + pic_info(album_url)[1] + '/' + str(i) + '/' + str(j) + '.jpg'
                # 图片下载目的完整路径
                pic_file_name = album_dir_name + '\\' + str(j) + '.jpg'
                # 获取到的图片文件
                pic_file = session.get(pic_url, headers=get_heades(i, j)).content
                # 写入文件
                save_pic(pic_file, pic_file_name)
        print('Done: ' + str(i) + ' ' + album_name + '\n')
        # 停顿几秒减轻服务器压力，同时也为了防止被封
        time.sleep(timesleep)
    print('\n' + '-' * 50 + '\n采集完成')


# 使用说明：
# get_album(<start>, <end=>, <timesleep>)
# <start>           起始编号，可不写，默认为 1
# <end>             结束编号，可不写，自动获取最大编号
# <timesleep>       暂停时间，可不写，减轻服务鸭梨，默认 30 秒
get_album(start=216, end=308, timesleep=30)
