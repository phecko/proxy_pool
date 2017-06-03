# -*- coding: utf-8 -*-
import json
import logging

from proxy_verify.verifier_manager import VerifierManager
from proxy_verify.schedule_manager import ScheduleManager
import multiprocessing
import time
import os
from proxy_verify.settings import settings
from scrapy.settings import Settings
import ip_proxy.settings as spider_settings
from scrapy.crawler import CrawlerProcess
from proxy_verify.utils import load_object
import socket


# socket.setdefaulttimeout(None)
spiders_status = multiprocessing.Manager().dict()
spiders_process_dict = multiprocessing.Manager().dict()



VERYFY_SLEEP_SECOND = 5
CHECK_SPIDER_SLEEP_SECOND = 15
PROXY_FRESH_SLEEP_SECOND = 20



class MainLoop(object):
    verifier_manager = None
    schedule_manager = None

    # cache spiders status

    crawl_process = None
    spiders_status = spiders_status
    spiders_process_dict = spiders_process_dict

    def __init__(self):
        self.verifier_manager = VerifierManager()
        self.schedule_manager = ScheduleManager(settings["MONGO_HOST"],settings["MONGO_PORT"])


    def run_verify(self):
        print "start verify loop"
        while(True):
            natures = self.schedule_manager.get_natures()

            if not natures:
                print "get no natures"
                time.sleep(VERYFY_SLEEP_SECOND)

            useful,useless = self.verifier_manager.verify(natures)

            self.schedule_manager.deal_results(useful,useless)
            print "finish one"
            time.sleep(VERYFY_SLEEP_SECOND)


    def run_refresh_old_proxy(self):
        print "start refresh old proxy"

        while (True):
            natures = self.schedule_manager.get_old_proxy(50)

            if not natures:
                print "get no natures"
                time.sleep(PROXY_FRESH_SLEEP_SECOND)

            useful, useless = self.verifier_manager.verify(natures)

            self.schedule_manager.deal_results(useful, useless,True)
            print "finish one"
            time.sleep(PROXY_FRESH_SLEEP_SECOND)

    def load_spiders_settings(self):
        file_path = os.path.join(os.path.join(os.path.dirname(__file__), "spiders.json"))
        try:
            with open(file_path,"r") as f:
                return json.load(f)
        except Exception as e:
            return {}

    def run_scrapy(self):
        while(True):
            print "start crawl proxy"

            cur_path = os.path.abspath("../ip_proxy")
            print cur_path

            spiders_setting = self.load_spiders_settings()

            cur_time = time.time()
            for spider_path,delta in spiders_setting.items():
                if spider_path in self.spiders_status:
                    print "check spider:",spider_path, delta, cur_time - self.spiders_status[spider_path][1],self.spiders_status[spider_path]

                    if self.spiders_status[spider_path][0]:
                        # last spider is not finished,pass
                        continue
                    elif cur_time - self.spiders_status[spider_path][1] < delta:
                        # smaller than time step
                        continue
                try:
                    spider_cls = load_object(spider_path)
                    self.spiders_status[spider_path] = [True,cur_time]
                    # self.run_scrapy_spider(spider_cls,spider_path)

                    self.run_scrapy_spider(spider_cls,spider_path)

                except Exception as e:
                    # if start spider fail ,just continue
                    logging.error(e)
                    continue

            time.sleep(CHECK_SPIDER_SLEEP_SECOND)

    def run_scrapy_spider(self,spider_cls,spider_path):
        print "start crawl proxy: %s" % spider_path

        def spider_finish_callback(result, spider_path,spiders_status):
            print "spider callback %s" % spider_path
            if spider_path in spiders_status:
                spiders_status[spider_path] = [False,spiders_status[spider_path][1]]
                print spiders_status

        def spider_err_callback(err, spider_path,spiders_status):
            print "spider callback %s" % spider_path
            if spider_path in spiders_status:
                spiders_status[spider_path] = [False,spiders_status[spider_path][1]]
                print spiders_status


        def run_spider(spiders_status):
            SpiderSettings = Settings()
            SpiderSettings.setmodule(spider_settings)
            SpiderSettings.set("MONGO_HOST", settings["MONGO_HOST"])
            SpiderSettings.set("MONGO_PORT", settings["MONGO_PORT"])
            crawl_process = CrawlerProcess(settings=SpiderSettings)
            crawl_process.crawl(spider_cls)
            crawl_process.start()
            deferred = crawl_process.join()
            # deferred.addCallback(spider_finish_callback,spider_path,spiders_status)
            deferred.addCallbacks(spider_finish_callback,
                                  errback=spider_err_callback,
                                  callbackArgs=(spider_path,spiders_status),
                                  errbackArgs=(spider_path,spiders_status))
        #     deferred.addErrback(spider_err_callback,spider_path,spiders_status)
        # pool = multiprocessing.Pool()
        # r = pool.map_async(run_spider,(self.spiders_status,),callback=callback)
        # r.wait()

        p = multiprocessing.Process(target=run_spider,args=(self.spiders_status,))
        # self.spiders_process_dict[spider_path]=p
        p.start()
        print "process is started :" + str(p.exitcode)

    def check_spiders_alive(self):
        while(True):
            for path,p in self.spiders_process_dict.items():
                if not p.is_alive and path in self.spiders_status:
                    logging.warning("spider is finish:"+path)
                    self.spiders_status[p][0] = False
                    del self.spiders_process_dict[p]
            time.sleep(5)





    def run(self):
        process1 = multiprocessing.Process(target=self.run_scrapy)

        process2 = multiprocessing.Process(target=self.run_verify)

        process3 = multiprocessing.Process(target=self.run_refresh_old_proxy)

        # process3 = multiprocessing.Process(target=self.check_spiders_alive)

        process1.start()
        process2.start()
        process3.start()
        # process3.start()

        process1.join()
        process2.join()
        process3.join()

if __name__ == '__main__':
    app = MainLoop()
    app.run()
