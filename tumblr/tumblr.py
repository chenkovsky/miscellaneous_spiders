#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通过scrapy下载
Usage:
    tumblr.py list <sites> <file>
    tumblr.py download <file> <dir>
"""
import sys
import re
import scrapy
from bs4 import BeautifulSoup
import os
from scrapy.http import Request
import xmltodict

class AppItem(scrapy.Item):
    category = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()

class TumblrSpider(scrapy.Spider):
    """
    Usage:
        scrapy runspider tumblr.py -a sites=s1,s2 [-a typ=photo|video|all]
    """
    name = "tumblr"
    base_url = "http://{0}.tumblr.com/api/read?type={1}&num={2}&start={3}"
    START = 0
    MEDIA_NUM = 50
    pattern = re.compile(r'[\S\s]*src="(\S*)" ')

    def header(self):
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        }

    def __init__(self, **kwargs):
        self.sites = kwargs["sites"].split(",")
        self.crawl_photo = True
        self.crawl_video = True
        if "typ" in kwargs:
            if "video" == kwargs["typ"]:
                self.crawl_video = False
            if "photo" == kwargs["typ"]:
                self.crawl_photo = False


    def start_requests(self):

        # Numbers of photos/videos per page
        if self.crawl_video:
            start = self.START
            for site in self.sites:
                url = self.base_url.format(site, "video", self.MEDIA_NUM ,start)
                yield Request(url, headers=self.header(), callback=self.parse, meta = {"typ": "video", "start" : start, "site": site})
        if self.crawl_photo:
            start = self.START
            for site in self.sites:
                url = self.base_url.format(site, "photo", self.MEDIA_NUM, start)
                yield Request(url, headers=self.header(), callback=self.parse, meta = {"typ": "photo", "start" : start, "site": site})

    def parse(self, response):
        data = xmltodict.parse(response.body)
        typ = response.meta["typ"]
        start = response.meta["start"]
        site = response.meta["site"]
        try:
            posts = data["tumblr"]["posts"]["post"]
            for post in posts:
                # select the largest resolution
                # usually in the first element
                p =  self.parse_post(typ, post, site)
                if p:
                    yield p
            start += self.MEDIA_NUM
            url = self.base_url.format(site, typ, self.MEDIA_NUM ,start)
            yield Request(url, headers=self.header(), callback=self.parse, meta={"typ":typ, "start":start, "site": site})
        except KeyError:
            pass

    def parse_post_url(self, typ, post):
        try:
            if typ == "photo":
                return post["photo-url"][0]["#text"]
            if typ == "video":
                video_player = post["video-player"][1]["#text"]
                match = self.pattern.match(video_player)
                if match is not None:
                    try:
                        return match.group(1)
                    except IndexError:
                        return None
        except:
            raise TypeError("Unable to find the right url for downloading. %s" % post)

    def parse_post(self, typ, post, site):
        medium_url = self.parse_post_url(typ, post)
        if medium_url is not None:
            medium_name = medium_url.split("/")[-1].split("?")[0]
            if typ == "video":
                if not medium_name.startswith("tumblr"):
                    medium_name = "_".join([medium_url.split("/")[-2],
                                            medium_name])
                medium_name += ".mp4"
            return {
                "typ" : typ,
                "site": site,
                "post": post,
                "url" : medium_url,
                "name": medium_name
            }
        return None

if __name__ == '__main__':
    downloader = "aria2c"
    from docopt import docopt
    import json
    args = docopt(__doc__)
    if args["list"]:
        args["<sites>"]
        cmd = "scrapy runspider tumblr.py -a sites=%s -o %s" % (args["<sites>"], args["<file>"])
        print(cmd)
        os.system(cmd)
    elif args["download"]:
        with open(args["<file>"]) as fi:
            js = json.load(fi)
        for post in js:
            url = post["url"]
            typ = post["typ"]
            site = post["site"]
            name = post["name"]
            dst_dir = os.path.join(args["<dir>"], site, typ)
            dst_file = os.path.join(dst_dir, name)
            if not os.path.exists(dst_dir):
                print("mkdir %s" % dst_dir)
                os.makedirs(dst_dir)
            if not os.path.exists(dst_file):
                cmd = "%s %s -o %s" % (downloader, url, dst_file)
                print(cmd)
                os.system(cmd)
