# -*- coding: utf-8 -*-
import json
import random

from flask import Flask,request,g
from pymongo import  *

app = Flask(__name__)

setting = {
    "MongoHost": "mongo",
    "MongoPort": 27017
}


@app.before_request
def connect_db():
    g.db = MongoClient(setting["MongoHost"],setting["MongoPort"])


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