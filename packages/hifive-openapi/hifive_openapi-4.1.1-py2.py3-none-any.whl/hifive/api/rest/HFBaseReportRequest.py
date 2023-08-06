'''
Created by yong.huang on 2016.11.04
'''
from hifive.api.base import RestApi


class HFBaseReportRequest(RestApi):
    def __init__(self, domain=None, port=80,method="POST"):
        domain = domain or 'hifive-gateway-test.hifiveai.com';
        RestApi.__init__(self, domain, port,method)
        self.clientId = None
        self.targetId = None
        self.action = None
        self.location = None
        self.context = None




    def getapiname(self):
        return 'BaseReport'
