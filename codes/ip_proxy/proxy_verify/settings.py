# -*- coding: utf-8 -*-

import os
import json


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