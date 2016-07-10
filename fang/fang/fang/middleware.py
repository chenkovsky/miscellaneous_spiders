__author__ = 'chenkovsky'
# setting variable
# PROXY_SERVER
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware
class SettingProxyMiddleware(HttpProxyMiddleware):
    def __init__(self, proxy_uri):
        super(SettingProxyMiddleware, self).__init__()
        self.proxy_uri = proxy_uri
    @classmethod
    def from_settings(cls, settings):
        proxy_uri = settings.get('PROXY_SERVER')
        return cls(proxy_uri)
    def process_request(self, request, spider):
        if self.proxy_uri:
            request.meta['proxy'] = self.proxy_uri
        else:
            super.process_request(request, spider)
        #request.meta['proxy'] = 'http://push.cootekservice.com:8080/'


import random
import os
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
class UserAgentsMiddleware(UserAgentMiddleware):
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        filename = crawler.settings.get('USER_AGENTS_LIST_FILE',os.path.dirname(os.path.realpath(__file__))+'/user-agents.txt')
        with open(filename) as f:
            user_agents = [
                line.strip()
                for line in f.readlines()
            ]
            return cls(user_agents)

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers.setdefault('User-Agent', user_agent)


import scrapy
import chardet
class ResponseCodecMiddleware(object):
    def process_response(request, response, spider):
        if response.status != 200 or type(response) != scrapy.http.TextResponse:
            #log.DEBUG("response is %d:%s" % (response.status, response.url))
            return response
        t = response.body
        content_type = chardet.detect(t)
        if content_type['encoding'] != "UTF-8":
            t = t.decode(content_type['encoding']).encode("UTF-8")
            response.body = t
            response.encoding = "UTF-8"
        return response