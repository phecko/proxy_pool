# -*- coding: utf-8 -*-

ANONYMITY_LEVEL_NORMAL = 5
ANONYMITY_LEVEL_HIGH = 1


class Proxy(object):
    def __init__(self,host="",port=80,scheme="HTTP",anonymity=5,speed=None,country=None,location=None):
        super(Proxy,self).__init__()
        self.host = host
        self.port = port
        self.scheme = scheme
        self.anonymity = anonymity
        self.speed = speed
        self.country = country
        self.location = location

    @property
    def identify(self):
        return  "%s:%d@%s" % (self.host,int(self.port),str(self.scheme))

    def __str__(self):
        return "%s:%d@%s level:%d" % (self.host,int(self.port),str(self.scheme),int(self.anonymity))

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return  "%s:%d@%s" % (self.host,int(self.port),str(self.scheme))

    def get_dict(self):
        return {
            "host": self.host,
            "port": self.port,
            "scheme": self.scheme,
            "anonymity": self.anonymity,
            "speed": self.speed,
            "country": self.country,
            "location": self.location,
            "identify": self.identify,
        }

    @classmethod
    def from_list_to_proxy(cls,proxys_list):
        results = []
        for info in proxys_list:
            if isinstance(info,dict):
                try:
                    proxy = cls(host=info["host"],port=info["port"],scheme=info["scheme"])
                    results.append(proxy)
                except Exception as e:
                    pass
            elif isinstance(info,(tuple,list)):
                try:
                    proxy = cls(*info)
                    results.append(proxy)
                except Exception as e:
                    pass
            elif isinstance(info,cls):
                results.append(info)

        return results
