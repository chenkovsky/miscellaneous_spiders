# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy import log
from scrapy.http.response.html import HtmlResponse
import bs4
import re
url_re = re.compile(r'p(\d+)')
class SecondHandItem(scrapy.Item):
    img = scrapy.Field()
    house_title = scrapy.Field()
    more_info = scrapy.Field()
    address = scrapy.Field()
    detail = scrapy.Field()
    price_total = scrapy.Field()

class SecondhandSpider(CrawlSpider):
    name = "secondhand"
    allowed_domains = ["shanghai.anjuke.com"]
    start_urls = ['http://shanghai.anjuke.com/sale/p2426/']#1982
    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse_it)
    def next_page_url(self, cur_page_idx):
        return "http://shanghai.anjuke.com/sale/p%d/" % (cur_page_idx+1)
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
        if "抱歉，没有找到符合要求的房源。" in response.body:
            print("-------------------")
            print(response.body)
            print("-------------------")
            print("抱歉，没有找到符合要求的房源。")#45244
            return
        soup = bs4.BeautifulSoup(response.body)
        for house in soup.select("ul#house-list li"):
            price_total = house.select("div.pro-price strong")[0].text.strip()
            img = house.select("img")[0]['src']
            house_title = house.select("div.house-title")[0].text.strip()
            #print("---------------")
            #print([x for x in house.select("div.house-details")])
            #print(len([x for x in house.select("div.house-details")]))
            #print("---------------")
            more_info = [y.text.strip() for y in [x for x in house.select("div.house-details > div")][1].select("span")]
            address = house.select("span.comm-address")[0].text.strip()
            detail = [x.text.strip() for x in house.select("div.details-bottom span")]
            yield SecondHandItem(img = img,
                            house_title = house_title,
                            more_info = more_info,
                            address = address,
                            detail = detail,
                            price_total = price_total)

        yield Request(next_url, callback=self.parse_it)
