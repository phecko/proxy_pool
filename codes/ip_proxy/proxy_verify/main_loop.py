# -*- coding: utf-8 -*-

from proxy_verify.verifier_manager import VerifierManager
from proxy_verify.schedule_manager import ScheduleManager
import multiprocessing
import time
import os


from ip_proxy.spiders.xicidaili import XicidailiSpider
from proxy_verify.settings import settings
# from scrapy import signals,log
# from twisted.internet import  reactor
# from scrapy.crawler import Crawler
from scrapy.settings import Settings
import ip_proxy.settings as spider_settings
from scrapy.crawler import CrawlerProcess


class MainLoop(object):
    verifier_manager = None
    schedule_manager = None

    def __init__(self):
        self.verifier_manager = VerifierManager()
        self.schedule_manager = ScheduleManager(settings["MONGO_HOST"],settings["MONGO_PORT"])


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
        SpiderSettings = Settings()
        SpiderSettings.setmodule(spider_settings)
        SpiderSettings.set("MONGO_HOST",settings["MONGO_HOST"])
        SpiderSettings.set("MONGO_PORT",settings["MONGO_PORT"])
        process = CrawlerProcess(settings=SpiderSettings)
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
