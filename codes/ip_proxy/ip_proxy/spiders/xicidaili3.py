# -*- coding: utf-8 -*-
import scrapy
import urlparse
from  ip_proxy.items import IpProxyItem

class XicidailiSpider3(scrapy.Spider):
    name = "xicidaili3"
    allowed_domains = ["xicidaili.com"]
    start_urls = ['http://www.xicidaili.com/nn/']


    custom_settings = {
        "ITEM_PIPELINES" : {
            'ip_proxy.pipelines.IpProxyPipeline': 300,
        }
    }


    def parse(self, response):

        ips = response.xpath('//table/tr/td[2]/text()').extract()
        ports = response.xpath('//table/tr/td[3]/text()').extract()
        anonymity = response.xpath('//table/tr/td[5]/text()').extract()
        scheme = response.xpath('//table/tr/td[6]/text()').extract()

        proxys = zip(ips,ports,scheme,anonymity)


        for proxy in proxys :

             yield IpProxyItem(host=proxy[0],port=proxy[1],scheme=proxy[2],anonymity=proxy[3])


        next_page = response.css('#body > div.pagination > em.current').xpath("following::a[1]/@href").extract_first()
        print next_page

        # from scrapy.shell import inspect_response
        # inspect_response(response, self)



        if next_page :
            next_page = urlparse.urljoin(response.url,next_page)
            # yield scrapy.Request(next_page)

        pass
