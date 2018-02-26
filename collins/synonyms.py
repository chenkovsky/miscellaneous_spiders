#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通过scrapy下载 www.collinsdictionary.com 的同义词
Usage:
    synonyms.py <vocab> <output>
"""
import sys
import re
import scrapy
from bs4 import BeautifulSoup
import os
from scrapy.http import Request


class SynonymsSpider(scrapy.Spider):
    """
    Usage:
        scrapy runspider synonyms.py -a vocab=vocab_file
    """
    name = "synonyms"
    base_url = "https://www.collinsdictionary.com/"\
        "dictionary/english-thesaurus/{phrase}"

    def header(self):
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        }

    def __init__(self, **kwargs):
        phrases = set()
        for fname in kwargs["vocab"].split(","):
            with open(fname) as fi:
                for l in fi:
                    phrases.add("-".join(l.split()))
        self.phrases = list(phrases)

    def start_requests(self):
        for phrase in self.phrases:
            yield Request(
                self.base_url.format(phrase=phrase),
                headers=self.header(),
                callback=self.parse,
                meta={"phrase": phrase, "page": 1})

    def parse(self, response):
        data = BeautifulSoup(response.body, "lxml")
        syns = response.meta.get("syns", [])
        for syn in data.select("div.type-syn"):
            orth = syn.select('.orth')[0].text
            syns.append(orth)
        for syn in data.select("div.moreSyn div.syns_head"):
            orth = syn.select('.orth')[0].text
            syns.append(orth)
        pages = data.select(".pagination .page")
        cur_page = response.meta["page"]
        cur_phrase = response.meta["phrase"]
        for i, page in enumerate(pages):
            if i >= cur_page:
                href = page["href"]
                if href:
                    yield Request(
                        href,
                        headers=self.header(),
                        callback=self.parse,
                        meta={"phrase": cur_phrase,
                              "syns": syns, "page": i + 1})
        if cur_page == len(pages) or len(pages) == 0:
            yield {"phrase": cur_phrase, "syns": syns}


if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)
    args["<vocab>"]
    cmd = "scrapy runspider synonyms.py -a vocab=%s -o %s" % (
        args["<vocab>"], args["<output>"])
    print(cmd)
    os.system(cmd)
