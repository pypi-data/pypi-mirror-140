'''
Created by yong.huang on 2016.11.04
'''
from hifive.api.base import RestApi
class HFOpenMemberSheetRequest(RestApi):
	def __init__(self, domain=None, port=80):
		domain = domain or 'hifive-gateway-test.hifiveai.com';
		RestApi.__init__(self,domain, port)
		self.accessToken = None
		self.page = None
		self.pageSize = None

	def getapiname(self):
		return 'MemberSheet'
