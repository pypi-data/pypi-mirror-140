'''
Created by yong.huang on 2016.11.04
'''
from hifive.api.base import RestApi
class HFTagSheetRequest(RestApi):
	def __init__(self, domain=None, port=80):
		domain = domain or 'hifive-gateway-test.hifiveai.com';
		RestApi.__init__(self,domain, port)
		self.clientId = None
		self.tagId = None
		self.type = None
		self.recoNum = None
		self.language = None

	def getapiname(self):
		return 'TagSheet'
