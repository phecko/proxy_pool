# -*- coding: utf-8 -*-

from proxy_verify.verifiers.mayidaili import MayidailiVerify

import time
from pymongo import *
import random
from proxy_verify.utils import load_object,to_list
from proxy_verify.models import Proxy





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




