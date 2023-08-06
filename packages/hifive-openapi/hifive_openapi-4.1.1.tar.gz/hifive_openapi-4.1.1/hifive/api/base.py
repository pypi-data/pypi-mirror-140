# -*- coding: utf-8 -*-
'''
Created on 2012-7-3

@author: lihao
'''

try:
    import httplib
except ImportError:
    import http.client as httplib
import hashlib
import hifive
import requests
import random
import itertools
import mimetypes
import base64
import hmac
import time
import sys
from hashlib import sha1

if sys.version.startswith("2"):
    from urllib import quote
else:
    from urllib.parse import quote


'''
定义一些系统变量
'''
SYSTEM_GENERATE_VERSION = "taobao-sdk-python-20160830"

X_HF_APPID = "X-HF-AppId"
P_API = "method"
X_HF_ACTION = "X-HF-Action"
X_HF_Token = "X-HF-Token"
X_HF_VERSION = "X-HF-Version"
X_HF_NONCE = "X-HF-Nonce"
X_HF_CLIENT_ID = "X-HF-ClientId"
AUTHORIZATION = "Authorization"
X_HF_TIMESTAMP = "X-HF-Timestamp"
HMAC_SHA1 = "HF3-HMAC-SHA1"
SIGNATURE = "Signature"
VERSION = "V4.1.1"
P_SESSION = "session"
P_ACCESS_TOKEN = "access_token"
P_VERSION = "v"
P_FORMAT = "format"
P_TIMESTAMP = "timestamp"
P_SIGN = "sign"
P_SIGN_METHOD = "sign_method"
P_PARTNER_ID = "partner_id"

P_CODE = 'code'
P_SUB_CODE = 'sub_code'
P_MSG = 'msg'
P_SUB_MSG = 'sub_msg'

N_REST = '/router/rest'


def sign(accessKeySecret, parameters, sign_header, method):
    # ===========================================================================
    # '''签名方法
    # @param secret: 签名需要的密钥
    # @param parameters: 支持字典和string两种
    # '''
    # ===========================================================================
    # 如果parameters 是字典类的话
    heards = method \
             + ' ' + sign_header[X_HF_ACTION] \
             + ' ' + sign_header[X_HF_VERSION] \
             + ' ' + sign_header[X_HF_APPID] \
             + ' ' + sign_header[X_HF_NONCE] \
             + ' ' + sign_header[X_HF_CLIENT_ID] \
             + ' ' + sign_header[AUTHORIZATION] \
             + ' ' + sign_header[X_HF_TIMESTAMP]

    headersBase64 = base64.b64encode(heards.encode()).decode()

    sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
    canonicalizedQueryString = ''
    for (k, v) in sortedParameters:
        if k == 'clientId':
            continue
        canonicalizedQueryString += '&' + k + '=' + v

    stringToSign = canonicalizedQueryString[1:]
    if (len(stringToSign) == 0):
        stringToSign = headersBase64
    else:
        stringToSign = stringToSign + "&" + headersBase64
    stringToSignBase64 = base64.b64encode(stringToSign.encode()).decode()
    h = hmac.new(accessKeySecret.encode(), stringToSignBase64.encode(), sha1).digest()

    m = hashlib.md5()
    m.update(h)
    sign = str(m.hexdigest()).upper()
    return sign


def percent_encode(encodeStr):
    encodeStr = str(encodeStr)
    res = quote(encodeStr.encode('utf-8').decode(sys.stdin.encoding), '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res


def mixStr(pstr):
    if (isinstance(pstr, str)):
        return pstr
    else:
        return str(pstr)


class FileItem(object):
    def __init__(self, filename=None, content=None):
        self.filename = filename
        self.content = content


class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = "PYTHON_SDK_BOUNDARY"
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, str(value)))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((mixStr(fieldname), mixStr(filename), mixStr(mimetype), mixStr(body)))
        return

    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary

        # Add the form fields
        parts.extend(
            [part_boundary,
             'Content-Disposition: form-data; name="%s"' % name,
             'Content-Type: text/plain; charset=UTF-8',
             '',
             value,
             ]
            for name, value in self.form_fields
        )

        # Add the files to upload
        parts.extend(
            [part_boundary,
             'Content-Disposition: file; name="{0}"; filename="{1}"'.format(field_name, filename),
             'Content-Type: {0}'.format(content_type),
             'Content-Transfer-Encoding: binary',
             '',
             body,
             ]
            for field_name, filename, content_type, body in self.files
        )

        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


class TopException(Exception):
    # ===========================================================================
    # 业务异常类
    # ===========================================================================
    def __init__(self):
        self.errorcode = None
        self.message = None
        self.subcode = None
        self.submsg = None
        self.application_host = None
        self.service_host = None

    def __str__(self, *args, **kwargs):
        sb = "errorcode=" + mixStr(self.errorcode) + \
             " message=" + mixStr(self.message) + \
             " subcode=" + mixStr(self.subcode) + \
             " submsg=" + mixStr(self.submsg) + \
             " application_host=" + mixStr(self.application_host) + \
             " service_host=" + mixStr(self.service_host)
        return sb


class RequestException(Exception):
    # ===========================================================================
    # 请求连接异常类
    # ===========================================================================
    pass


class RestApi(object):
    # ===========================================================================
    # Rest api的基类
    # ===========================================================================

    def __init__(self, domain='gw.api.taobao.com', port=80, method=None):
        # =======================================================================
        # 初始化基类
        # Args @param domain: 请求的域名或者ip
        #      @param port: 请求的端口
        # =======================================================================
        self.__domain = domain
        self.__port = port
        self.__httpmethod = method or "GET"
        self.__token = None
        self.version = VERSION
        if (hifive.getDefaultAppInfo()):
            self.__app_key = hifive.getDefaultAppInfo().appkey
            self.__secret = hifive.getDefaultAppInfo().secret
            self.__token = hifive.getDefaultAppInfo().token

    def get_request_header(self):
        return {}

    def set_app_info(self, appinfo):
        # =======================================================================
        # 设置请求的app信息
        # @param appinfo: import top
        #                 appinfo top.appinfo(appkey,secret)
        # =======================================================================
        self.__app_key = appinfo.appkey
        self.__secret = appinfo.secret
        self.__token = appinfo.token


    def set_app_version(self, version):
        # =======================================================================
        # 设置请求的app信息
        # @param appinfo: import top
        #                 appinfo top.appinfo(appkey,secret)
        # =======================================================================
        self.version = version

    def getapiname(self):
        return ""

    def getNonce(self):
        return "".join(random.sample(
            ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f',
             'e', 'd', 'c', 'b', 'a', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 32))

    def getTimestamp(self):
        return str(int(round(time.time() * 1000)))

    def getMultipartParas(self):
        return []

    def getTranslateParas(self):
        return {}

    def _check_requst(self):
        pass

    def getResponse(self, timeout=30):
        # =======================================================================
        # 获取response结果
        # =======================================================================
        method = self.__httpmethod.upper()
        sys_headers = {
            X_HF_ACTION: self.getapiname(),
            X_HF_VERSION: self.version,
            X_HF_APPID: self.__app_key,
            X_HF_NONCE: self.getNonce(),
            X_HF_CLIENT_ID: self.__dict__["clientId"],
            AUTHORIZATION: HMAC_SHA1,
            X_HF_TIMESTAMP: self.getTimestamp(),
        }

        sys_parameters = {
        }

        application_parameter = self.getApplicationParameters()
        header = self.get_request_header()

        sign_parameter = sys_parameters.copy()
        sign_parameter.update(application_parameter)

        sign_header = sys_headers.copy()
        sign_header.update(sign_header)
        signature = sign(self.__secret, sign_parameter, sign_header, method)

        # 计算签名
        # sys_headers[P_SIGN] = sign_header[AUTHORIZATION]+" "+"Signature="+signature)
        sys_headers[AUTHORIZATION] = sign_header[AUTHORIZATION] + " " + "Signature=" + signature
        if self.__token is not None:
            sys_headers[X_HF_Token] = self.__token
        # 下面开始请求
        header.update(sys_headers)

        del application_parameter["clientId"]
        sys_parameters.update(application_parameter)
        data = sys_parameters

        if (self.getMultipartParas()):
            form = MultiPartForm()
            files = {}

            for key in self.getMultipartParas():
                files[key] = self.__dict__[key]

            return requests.post(self.__domain, files=files, data=sys_parameters).json()

        if (method == 'GET'):
            resp = requests.get(self.__domain, data, headers=header, timeout=timeout)
        else:
            resp = requests.post(self.__domain, data, headers=header, timeout=timeout)
        if not resp:
            raise RequestException("connection error,response code:{0}.".format(resp.status_code))
        return resp.json()

    def getApplicationParameters(self):
        application_parameter = {}
        for key, value in self.__dict__.items():
            if not key.startswith("__") and key not in self.getMultipartParas() and not key.startswith(
                    "_RestApi__") and value is not None:
                if (key.startswith("_")):
                    application_parameter[key[1:]] = value
                else:
                    application_parameter[key] = value
        # 查询翻译字典来规避一些关键字属性
        translate_parameter = self.getTranslateParas()
        for key, value in application_parameter.items():
            if key in translate_parameter:
                application_parameter[translate_parameter[key]] = application_parameter[key]
                del application_parameter[key]
        return application_parameter
