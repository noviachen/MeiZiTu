# -*- coding:utf-8 -*-

import os
import requests
import time
from bs4 import BeautifulSoup

# MZITU 首页链接地址
index_url = 'http://www.mzitu.com/'
# 默认存储文件夹
album_dir = 'C:\\Users\\novia\\Documents\\IMG\\MZITU\\'

session = requests.session()
s = session.post(index_url)

#去除特殊字符防止无法建立文件夹
def rpl_str(album_name):
    for i in ['?','？']:
        album_name=album_name.replace(i,'')
    return album_name



    # 组合 headers 不然显示的是盗链图片


def get_headers(album_url, pic_page):
    if pic_page > 1:
        ref = album_url + '/' + str(pic_page)
    else:
        ref = album_url
    headers = {
        'Accept': 'image/png, image/svg+xml, image/jxr, image/*;q=0.8, */*;q=0.5',
        'Accept-Language': 'zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.6,en;q=0.4,ja;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'i.meizitu.net',
        'Connection': 'Keep-Alive',
        'Referer': ref
    }
    return headers


# 存储图片
def save_pic(pic_file, pic_to_dir):
    fo = open(pic_to_dir, 'wb')
    fo.write(pic_file)
    fo.close()


# 获取最大页面数量
def max_pages():
    bs_obj = BeautifulSoup(session.get(index_url).text, 'html.parser')
    pages = bs_obj.find('div', {'class': 'nav-links'}).find_all('a')
    page_list = []
    for page in pages:
        page_list.append(page.get_text())
    return int(page_list[-2])


# 获取每个页面的图集链接列表
def album_urls(page):
    page_url = index_url + 'page/' + str(page) + '/'
    bs_obj = BeautifulSoup(session.get(page_url).text, 'html.parser')
    albums = bs_obj.find('ul', {'id': 'pins'}).find_all('a')
    albums = albums[::2]
    album_list = []
    for album in albums:
        album_list.append(album.attrs['href'])
    return album_list


# 获取图集最大图片数量
def max_pics(album_url):
    bs_obj = BeautifulSoup(session.get(album_url).text, 'html.parser')
    pages = bs_obj.find('div', {'class': 'pagenavi'}).find_all('a')
    page_list = []
    for page in pages:
        page_list.append(page.get_text())
    return int(page_list[-2])


# 获取图集中图片链接列表
def pic_urls(album_url):
    bs_obj = BeautifulSoup(session.get(album_url).text, 'html.parser')
    meta = bs_obj.find('div', {'class': 'main-meta'}).find_all('span')[1].get_text()
    a_or_b = bs_obj.find('div', {'class': 'main-image'}).find('img')['src'][-7]
    album_date = meta[4:14].replace('-', '/')
    pic_urls_list = []
    for i in range(1, max_pics(album_url) + 1):
        pic_url = 'http://i.meizitu.net/' + album_date + a_or_b + str(i).zfill(2) + '.jpg'
        pic_urls_list.append(pic_url)
    return pic_urls_list


# 图集文件夹名称
def album_name(album_url):
    bs_obj = BeautifulSoup(session.get(album_url).text, 'html.parser')
    title = bs_obj.h2.get_text()
    return title


# 主程序，下载图集到本地
def get_albums(start=1, end=max_pages(), timesleep=30):
    print('开始采集 MZITU ...\n' + '-' * 50 + '\n')
    for page in range(start, end + 1):
        for album_url in album_urls(page):
            album__name = rpl_str(album_name(album_url))
            album_id = album_url.replace('http://www.mzitu.com/', '')
            album_dir_name = album_dir + str(album_id) + ' ' + album__name
            if os.path.exists(album_dir_name):
                print(str(album_id) + ' ' + album__name + ' 已抓取过\n')
            else:
                print('Processing: ' + str(album_id) + ' ' + album__name)
                os.makedirs(album_dir_name)
                for pic_url in pic_urls(album_url):
                    pic_page = pic_url[-6:-4]
                    if int(pic_page[0]) == 0:
                        pic_page = int(pic_page[1])
                    else:
                        pic_page = int(pic_page)
                    pic_file = session.get(pic_url, headers=get_headers(album_url, pic_page)).content
                    pic_to_dir = album_dir_name + '\\' + str(pic_page) + '.jpg'
                    save_pic(pic_file, pic_to_dir)
                print('Done: ' + str(album_id) + ' ' + album__name + '\n')
            time.sleep(timesleep)
        print('Page ' + str(page) + ' is Done\n')
        time.sleep(timesleep * 3)
    print('\n' + '-' * 50 + '\n采集完成')


# 使用说明：
# get_album(<start>, <end=>, <timesleep>)
# <start>           起始页码，可不写，默认为 1
# <end>             结束页码，可不写，自动获取最大编号
# <timesleep>       暂停时间，可不写，减轻服务鸭梨，默认 30 秒
# 因为链接的编号不是你按照顺序，没法像 MMJPG 那样操作，所以只能按照一页一页去分割
get_albums(start=5, timesleep=5)
