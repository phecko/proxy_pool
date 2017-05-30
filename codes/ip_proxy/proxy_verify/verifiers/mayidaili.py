# -*- coding: utf-8 -*-
import json

from proxy_verify.core import VerifierBase
from proxy_verify.models import  Proxy
import requests
import  time



class MayidailiVerify(VerifierBase):

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    get_info_url = 'http://www.mayidaili.com/proxy/get-proxy-info/'
    add_url = 'http://www.mayidaili.com/proxy/add-proxy/'

    def __init__(self,max_try=2,*args,**kwargs):
        super(MayidailiVerify,self).__init__(*args,**kwargs)
        self.max_try = max_try

    def verify_proxy(self, host, port, scheme):

        return self.verify_proxy_list((host,port))[0]

    def verify_proxy_list(self, proxies):
        '''
        :param proxies: a list of tuple (host,port,scheme) or Proxy
        :return: a list of  (useful,Proxy)
        '''

        if not proxies:
            return

        if len(proxies) > 50:
            proxies = proxies[:50]

        proxies = Proxy.from_list_to_proxy(proxies)
        length = len(proxies)
        finished = 0
        results = [[False,v] for v in proxies]

        addData = "\n".join([v.host+":"+v.port for v in proxies])

        print "start to verify\n"

        addR = requests.post(url=self.add_url,data=addData)

        time.sleep(2)

        gets_proxies = proxies[:]

        for try_time in xrange(self.max_try):
            data = {"proxys": json.dumps([{"host": v.host, "port":v.port} for v in gets_proxies])}

            r = requests.post(self.get_info_url,data)

            print "test %d times\n" % try_time

            if not r.content:
                time.sleep(1)
                continue

            gets = r.json()
            gets = gets["data"]
            finished += len(gets)
            print "Test %d ,get %d" % (len(proxies),len(gets))
            for i,proxy in enumerate(proxies):
                for one in gets:
                    if unicode(one["host"])==unicode(proxy.host) and unicode(one["port"]) == unicode(proxy.port):
                        cur_proxy = results[i][1]
                        results[i][0] = True
                        cur_proxy.anonymity = one["anonymous_level"]
                        cur_proxy.speed = one["n0"]
                        cur_proxy.country = one["country"]
                        cur_proxy.location = one["city"]

            if finished==length:
                break

            new_proxy = []
            for i,r in enumerate(results):
                if r[0] == False:
                    new_proxy.append(proxies[i])
            gets_proxies = new_proxy

            time.sleep(1)

        return results



if __name__ == '__main__':

    verify = MayidailiVerify()
    proxys = [
    ("180.118.99.99","8118"),
    ("116.226.90.12","808"),
    ("36.45.145.15","8998"),
    ("114.248.98.47","8118"),
    ("115.203.76.188","808"),
    ("112.195.49.109","808"),
    ("58.253.70.149","8080"),
    ("139.224.237.33","8888"),
    ("220.166.96.90","82"),
    ("175.155.242.123","808"),
    ("1.194.171.87","808"),
    ("112.194.45.229","808"),
    ("111.72.230.106","808"),
    ("115.215.70.57","808"),
    ("221.10.159.234","1337"),
    ("221.229.47.152","808"),
    ("49.86.62.54","808"),
    ("218.64.92.63","808"),
    ("183.153.54.68","808"),
    ("117.43.1.253","808"),
    ("27.29.42.101","808"),
    ("61.232.254.39","3128"),
    ("182.122.113.204","8118"),
    ("119.48.180.124","8118"),
    ("183.1.86.138","8118"),
    ("221.229.47.66","808"),
    ("180.118.240.98","808"),
    ("203.93.0.115","80"),
    ("114.239.1.21","808"),
    ("121.226.169.27","808"),
    ("211.83.247.153","8998"),
    ("119.5.0.22","808"),
    ("114.239.151.194","808")
    ]

    results = verify.verify_proxy_list(proxys)
    print results