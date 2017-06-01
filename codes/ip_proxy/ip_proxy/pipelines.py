# -*- coding: utf-8 -*-

import logging
import datetime
from pymongo import  *

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class IpProxyPipeline(object):

    mongoClient = None

    def __init__(self,host,port):
        logging.debug("Open Mongo %s:%d" % (host,port))
        self.mongoClient= MongoClient(host,port)

    def process_item(self, item, spider):
        db = self.mongoClient["ip_proxy"]["nature_proxy"]
        item["last_update"] = datetime.datetime.now()
        logging.debug("insert One")
        db.update_one({"update_at": item["last_update"]}, {"$set": dict(item)}, upsert=True)

        # return item

    def close_spider(self, spider):
        logging.debug("Close Mongo")
        self.mongoClient.close()


    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings

        logging.debug("Connect Mongo")

        return cls(settings["MONGO_HOST"], settings["MONGO_PORT"])
