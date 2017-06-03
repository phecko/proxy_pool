# -*- coding: utf-8 -*-
import time
from pymongo import *
from threading import Lock

class ScheduleManager(object):


    mongoClient = None
    readLock = Lock()

    def __init__(self,mongo_host,mongo_port):
        super(ScheduleManager,self).__init__()
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port
        # self.mongoClient = MongoClient(mongo_host,mongo_port)

    def get_natures(self,count=50):
        self.readLock.acquire()
        client = MongoClient(self.mongo_host,self.mongo_port)
        db = client.get_database("ip_proxy")
        col = db.get_collection("nature_proxy")
        natures = col.find(limit=count)
        natures = [ v for v in natures]
        if not natures or len(natures) <= 0:
            self.readLock.release()
            return None
        ids = [v[u"_id"] for v in natures]
        delR = col.delete_many({"_id": {"$in" : ids}})

        self.readLock.release()
        client.close()
        return natures

    def get_old_proxy(self, count=50):
        client = MongoClient(self.mongo_host, self.mongo_port)
        db = client.get_database("ip_proxy")
        col = db.get_collection("proxy")
        proxys = col.find(limit=count).sort([("update_at", ASCENDING)])
        proxys = list(proxys)
        client.close()
        return proxys

    def deal_results(self,useful,useless,remove_useless=False):
        client = MongoClient(self.mongo_host, self.mongo_port)
        col = client["ip_proxy"]["proxy"]
        print "start to deal"
        for use_one in useful:
            d = use_one.get_dict()
            d.update({"update_at":time.time()})
            col.update_one({"identify":use_one.identify},{"$set":d},upsert=True)

        if remove_useless and len(useless) > 0:
            ids = [use.identify for use in useless]
            delR = col.delete_many({"identify": {"$in":ids}})
            print delR.deleted_count

        client.close()

