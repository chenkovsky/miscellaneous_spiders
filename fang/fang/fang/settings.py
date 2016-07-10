# -*- coding: utf-8 -*-

# Scrapy settings for fang project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'fang'

SPIDER_MODULES = ['fang.spiders']
NEWSPIDER_MODULE = 'fang.spiders'

DOWNLOADER_MIDDLEWARES = {
    # we'll turn off standart user agent middleware
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'fang.middleware.UserAgentsMiddleware': 400,
    #'fang.middleware.ResponseCodecMiddleware':400
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'fang (+http://www.yourdomain.com)'
