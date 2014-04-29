__author__ = 'suuuch'
#-*-coding:utf-8-*-
import urllib2
from bs4 import BeautifulSoup

target_url = "http://item.taobao.com/item.htm?id=24215144979"

page = urllib2.urlopen(target_url)
soup = BeautifulSoup(page)

attributes = soup.find("div","attributes")

ul = attributes.find("ul")
lis = ul.findAll("li")

for li in lis :

    print li.string