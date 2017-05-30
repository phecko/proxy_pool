# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IpProxyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    host = scrapy.Field()

    port = scrapy.Field()

    scheme = scrapy.Field()

    anonymity = scrapy.Field()

    last_update = scrapy.Field()

    @property
    def proxy(self):
        return self.host+":"+self.port

    pass
