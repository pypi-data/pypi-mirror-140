'''
Created on 2012-6-29

@author: lihao
'''
from hifive.api.base import sign



class appinfo(object):
    def __init__(self,appkey,secret,token=None):
        self.appkey = appkey
        self.secret = secret
        self.token = token
        
def getDefaultAppInfo():
    pass

     
def setDefaultAppInfo(appkey,secret,token=None):
    default = appinfo(appkey,secret,token)
    global getDefaultAppInfo 
    getDefaultAppInfo = lambda: default
    




    

