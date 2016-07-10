# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy import log
from scrapy.http.response.html import HtmlResponse
import bs4
import re
url_re = re.compile(r'p=(\d+)')
class FirstHandItem(scrapy.Item):
    infos = scrapy.Field()
    price = scrapy.Field()

class FirsthandSpider(CrawlSpider):
    name = "firsthand"
    allowed_domains = ["sh.fang.anjuke.com"]
    start_urls = ['http://sh.fang.anjuke.com/loupan/s?p=1']#1982
    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse_it)
    def next_page_url(self, cur_page_idx):
        return "http://sh.fang.anjuke.com/loupan/s?p=%d" % (cur_page_idx+1)
    def parse_it(self, response):
        if type(response) != scrapy.http.HtmlResponse:
            yield Request(response.url, callback=self.parse_it)
            return
        if response.status != 200:
            log.DEBUG("response is %d:%s" % (response.status, response.url))
            yield Request(response.url, callback=self.parse_it)
            return
        #print("----------------------"+response.url)
        page_idx = int(url_re.search(response.url).group(1))
        next_url = self.next_page_url(page_idx)
        soup = bs4.BeautifulSoup(response.body)
        has = False
        for house in soup.select("div.key-list div.item-mod div.estate-mod"):
            print(house.select("div.infos"))
            infos = house.select("div.infos")[0].text
            if len(house.select("div.favor span.price")) > 0:
                price = house.select("div.favor span.price")[0].text
            else:
                price = None
            yield FirstHandItem(infos = infos, price = price)
            has = True
        if has:
            yield Request(next_url, callback=self.parse_it)
