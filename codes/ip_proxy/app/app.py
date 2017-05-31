# -*- coding: utf-8 -*-
import json
import random
import os

from flask import Flask,request,g
from pymongo import  *

app = Flask(__name__)


def load_setting():
    setting = {}
    file_path = os.path.abspath( os.path.join(os.path.dirname(__file__),"../"))
    if "PROXY_POOL_ENV" in os.environ and os.environ["PROXY_POOL_ENV"] == "product":
        file_path = os.path.join(file_path, "product.conf")
    else:
        file_path = os.path.join(file_path, "dev.conf")

    try:
        with open(file_path,"rb") as f:
            setting = json.load(f)
    except Exception as e:
        file_name = os.path.basename(file_path)
        print "setting file %s is invalid\n %s" % (file_name,e)
        os._exit(127)

    return setting

settings = load_setting()


@app.before_request
def connect_db():
    g.db = MongoClient(settings["MONGO_HOST"],settings["MONGO_PORT"])


@app.teardown_request
def close_db(exception):
    if hasattr(g,"db"):
        if g.db :
            g.db.close()



@app.route("/get_proxy/")
def get_proxy():

    col = g.db["ip_proxy"]["proxy"]

    scheme =  request.args.get("scheme",None)
    anonymity = int(request.args.get("anonymity",0))
    count = int(request.args.get("count",10))

    filters = {}

    if scheme and scheme in ["HTTP","HTTPS","SOCK"]:
        filters["scheme"] = scheme

    if anonymity > 0 :
        filters["anonymity"] = anonymity

    total = col.count()

    start = 0

    if total > count:
        start = random.randint(0,total-count)

    select = col.find(filters,skip=start,limit=count)
    t = [v for v in select]
    results = [{"host": v[u'host'], "port":v[u'port'], "scheme":v[u'scheme'], "anonymity":v[u'anonymity'],"identify":v[u'identify']} \
               for v in t ]

    return json.dumps(results)


@app.route("/del_proxy/")
def del_proxy():
    mongoClient = MongoClient(setting["MongoHost"], setting["MongoPort"])
    col = mongoClient["ip_proxy"]["proxy"]

    proxys = request.args.get("proxys", None)

    if not proxys:
        return json.dumps({"del_count":0})

    proxys = str(proxys).split(",")

    del_count = 0

    for identify in proxys :
        dr = col.delete_many({"identify":identify})
        del_count += dr.deleted_count

    return json.dumps({"del_count":del_count})

if __name__ == '__main__':
    app.run()
