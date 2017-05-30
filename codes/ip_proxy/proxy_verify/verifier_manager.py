# -*- coding: utf-8 -*-

from proxy_verify.verifiers.mayidaili import MayidailiVerify

import time
from pymongo import *
import random
from proxy_verify.models import Proxy

def load_object(path):
    """Load an object given its absolute object path, and return it.

    object can be a class, function, variable o instance.
    path ie: 'scrapy.contrib.downloadermiddelware.redirect.RedirectMiddleware'
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError, "Error loading object '%s': not a full path" % path

    module, name = path[:dot], path[dot+1:]
    try:
        mod = __import__(module, {}, {}, [''])
    except ImportError, e:
        raise ImportError, "Error loading object '%s': %s" % (path, e)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError, "Module '%s' doesn't define any object named '%s'" % (module, name)

    return obj

def to_list(obj):
    if isinstance(obj,(tuple,list)):
        return obj
    return [obj]


class VerifierManager(object):

    settings = {'verifiers':[ 'proxy_verify.verifiers.mayidaili.MayidailiVerify']}

    verifiers = []


    def __init__(self):
        for verfier in self.settings["verifiers"]:
            v = load_object(verfier)
            self.verifiers.append(v())


    def verify(self,proxys):
        proxys = Proxy.from_list_to_proxy(to_list(proxys))
        # proxys = set(proxys)
        n = 50
        proxys_list = [proxys[i:i + n] for i in range(0, len(proxys), 50)]

        useful = []
        useless = []

        for pl in proxys_list:
            verifier = self.verifiers[0]
            results = verifier.verify_proxy_list(pl)
            for r in results:
                if r[0]==True:
                    useful.append(r[1])
                else :
                    useless.append(r[1])

        return useful,useless




