# -*- coding: utf-8 -*-

from proxy_verify.verifier_manager import VerifierManager
from proxy_verify.schedule_manager import ScheduleManager
import multiprocessing
import time
import os


from ip_proxy.spiders.xicidaili import XicidailiSpider
# from scrapy import signals,log
# from twisted.internet import  reactor
# from scrapy.crawler import Crawler
from scrapy.settings import Settings
import ip_proxy.settings as spider_settings
from scrapy.crawler import CrawlerProcess

mongo_settings = ["mongo",27017]

class MainLoop(object):
    verifier_manager = None
    schedule_manager = None

    def __init__(self):
        self.verifier_manager = VerifierManager()
        self.schedule_manager = ScheduleManager(mongo_settings[0],mongo_settings[1])


    def run_verify(self):
        print "start verify loop"
        while(True):
            natures = self.schedule_manager.get_natures()

            if not natures:
                print "get no natures"
                time.sleep(5)

            useful,useless = self.verifier_manager.verify(natures)

            self.schedule_manager.deal_results(useful,useless)
            print "finish one"
            time.sleep(5)

    def run_scrapy(self):

        while(True):
            print "start crawl proxy"

            cur_path = os.path.abspath("../ip_proxy")
            print cur_path

            # os.system()
            self.run_scrapy_spider(XicidailiSpider)

            print "sleep a day"
            time.sleep(86400)

    def run_scrapy_spider(self,spider_cls):
        settings = Settings()
        settings.setmodule(spider_settings)
        settings.set("MONGO_HOST",mongo_settings[0])
        settings.set("MONGO_PORT",mongo_settings[1])
        process = CrawlerProcess(settings=settings)
        process.crawl(spider_cls)
        process.start()


    def run(self):
        process1 = multiprocessing.Process(target=self.run_scrapy)

        process2 = multiprocessing.Process(target=self.run_verify)


        process1.start()
        process2.start()

        process1.join()
        process2.join()




if __name__ == '__main__':
    app = MainLoop()
    app.run()