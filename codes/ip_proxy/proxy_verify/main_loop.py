# -*- coding: utf-8 -*-
import json
import logging

from proxy_verify.verifier_manager import VerifierManager
from proxy_verify.schedule_manager import ScheduleManager
import multiprocessing
import time
import os
from ip_proxy.spiders.xicidaili import XicidailiSpider
from proxy_verify.settings import settings
from scrapy.settings import Settings
import ip_proxy.settings as spider_settings
from scrapy.crawler import CrawlerProcess
from proxy_verify.utils import load_object



class MainLoop(object):
    verifier_manager = None
    schedule_manager = None

    # cache spiders status
    spiders_signals = {}

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

    def load_spiders_settings(self):
        file_path = os.path.join(os.path.join(os.path.dirname(__file__), "spiders.json"))
        try:
            with open(file_path,"r") as f:
                return json.load(f)
        except :
            return {}

    def run_scrapy(self):

        while(True):
            print "start crawl proxy"

            cur_path = os.path.abspath("../ip_proxy")
            print cur_path

            # os.system()
            spiders_setting = self.load_spiders_settings()

            cur_time = time.time()
            for spider_path,delta in spiders_setting.items():
                if spider_path in self.spiders_signals:
                    if self.spiders_signals[spider_path][0]:
                        # last spider is not finished,pass
                        continue
                    elif cur_time - self.spiders_signals[spider_path][1] < spider_settings[spider_path]:
                        # smaller than time step
                        continue
                try:
                    spider_cls = load_object(spider_path)
                    self.spiders_signals[spider_path] = [True,cur_time]
                    self.run_scrapy_spider(spider_cls)
                except Exception as e:
                    # if start spider fail ,just continue
                    logging.error(e)
                    continue

            time.sleep(10)

    def run_scrapy_spider(self,spider_cls):
        SpiderSettings = Settings()
        SpiderSettings.setmodule(spider_settings)
        SpiderSettings.set("MONGO_HOST",settings["MONGO_HOST"])
        SpiderSettings.set("MONGO_PORT",settings["MONGO_PORT"])
        process = CrawlerProcess(settings=SpiderSettings)
        process.crawl(spider_cls)
        process.start()

        defered = process.join()
        print "finish"
        print defered


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