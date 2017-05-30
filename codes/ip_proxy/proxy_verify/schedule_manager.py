# -*- coding: utf-8 -*-

from pymongo import *
from threading import Lock

class ScheduleManager(object):


    mongoClient = None
    readLock = Lock()

    def __init__(self,mongo_host,mongo_port):
        super(ScheduleManager,self).__init__()
        self.mongoClient = MongoClient(mongo_host,mongo_port)


    def get_natures(self,count=50):
        self.readLock.acquire()
        db = self.mongoClient.get_database("ip_proxy")
        col = db.get_collection("nature_proxy")
        natures = col.find(limit=count)
        natures = [ v for v in natures]
        if not natures or len(natures) <= 0:
            return None
        # ids = [v[u"_id"] for v in natures]
        for v in natures:
            delR = col.delete_one({"_id": v["_id"]})

        self.readLock.release()
        return natures


    def deal_results(self,useful,useless):
        col = self.mongoClient["ip_proxy"]["proxy"]
        print "start to deal"
        for use in useful:
            col.update_one({"identify":use.identify},{"$set":use.get_dict()},upsert=True)


