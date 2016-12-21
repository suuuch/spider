# coding: utf-8
import requests
from bs4 import BeautifulSoup

import time


def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(int(value))
    ## 经过localtime转换后变成
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt


def fetch_article_content(query, page=1):
    base_url = 'http://weixin.sogou.com/weixin'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                                AppleWebKit/537.36 \
                                (KHTML, like Gecko)Chrome/54.0.2840.99 Safari/537.36'}
    payload = {
        'type': 2,
        'query': query,
        'ie': 'utf8',
        'page': page
    }
    content = requests.get(base_url, params=payload, headers=headers)
    soup = BeautifulSoup(content.text, 'lxml')
    news_list = soup.find('ul', attrs={'class': 'news-list'})
    li_list = news_list.find_all('li')

    article_list = []
    for li in li_list:
        article_items = {}
        article_items['href'] = li.find_all('a')[0]['href']
        article_items['img'] = li.find_all('img')[0]['src']
        article_items['title'] = li.find('h3').text.strip()
        article_items['desc'] = li.find('p', attrs={'class': 'txt-info'}).text
        article_items['source_wx'] = li.find('div', attrs={'class': 's-p'}).find('a').text
        article_items['pub_time'] = timestamp_datetime(li.find('div', attrs={'class': 's-p'})['t'])
        article_list.append(article_items)
    return article_list

data = fetch_article_content('大数据')
print(data)
