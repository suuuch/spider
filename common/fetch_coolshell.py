__author__ = 'such'
#-*-coding:utf-8-*-
'''获取coolshell.cn博文分类的连接'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib2
import urlparse
from bs4 import BeautifulSoup
sys.path.append(".")
import mysql_conn


def insert_data(urls):

    mysql_local = mysql_conn.mysql_connect()
    for name,url in urls.items():

        pages = get_art_page(url)
        for page in pages:
            m = get_art_url(page)
            for i in m:
                sql_content = "insert into article_sup values ( %s , %s )"
                data = (i['id'],i['href'])

                result = mysql_local.inser_data(sql_content,data)
                if result != 0 :
                    return result
                sql_content1 = "insert into article values ( %s , %s ,%s ,%s ,%s )"
                data = (i['id'],i['title'],int(name),'CoolShell',get_content(i['href']))
                result = mysql_local.inser_data(sql_content1,data)
                if result != 0 :
                    return result
    return 0



def split_path(path):
    str = path.split('/')

    if str[-1].find("."):
        str.extend(str.pop().split("."))
    return str


def get_art_page(url):

    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    pagenav = soup.find("div",id="pagenavi")
    pages = pagenav.find_all("a",class_="larger")
    data = [url,]
    for page in pages:
       data.append(page['href'])
    return data

def get_art_url(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    items = soup.find_all("div","post")
    link = []
    for item in items:
        data = dict()
        h2 = item.find("h2")
        data['title'] = h2.find("a").string
        data['href'] = h2.find("a")['href']
        url_parse  = urlparse.urlparse(data['href'])
        data['id'] = split_path(url_parse[2])[-2]
        link.append(data)
    return link

def get_content(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    items = soup.find("div",id = "content").find("div","content")
    clear_jiathis_style = items.find("div","jiathis_style")
    clear1 = clear_jiathis_style.find_previous("div")
    clear1.clear()
    return items
