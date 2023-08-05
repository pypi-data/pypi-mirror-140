# coding=utf-8
# Tools Libs, include generate signature, data encryption and decryption
# pip install pycryptodome
import logging

import hashlib
import base64
import hmac
import json

import requests
from Crypto.Cipher import AES
import time
from vaassdk.src.vaas import config


class Tools(object):
    def __init__(self, udid):
        self.dict = {}
        self.udid = udid

    # 入参以字典形式传入
    def set_input(self, dist):
        self.dict = dist

    # sha256加密获取签名
    def sha256_signature(self, aAesMes, aAccessToken, aTimeStamp):
        message = aAesMes
        secret_key = bytes(aAccessToken + str(aTimeStamp), 'utf-8')
        sign = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
        return sign

    # 数据加密
    def aes_encrypt(self, aAccessToken, aOriginText):
        key = bytes(aAccessToken, 'utf-8')
        iv = key[0:16]
        aes_padding = AES.block_size
        plain_text = aOriginText
        amount_to_pad = aes_padding - (len(plain_text) % aes_padding)
        if amount_to_pad == 0:
            amount_to_pad = aes_padding
        plain_text = bytes(plain_text + chr(amount_to_pad) * amount_to_pad, 'utf-8')
        cryptor = AES.new(key, AES.MODE_CBC, iv)
        en_text = base64.b64encode(cryptor.encrypt(plain_text))
        return en_text

    # 数据解密
    def aes_decrypt(self, aAESData, aToken):
        if aAESData == "":
            logging.warning("the data is empty")
            return []

        key = bytes(aToken, 'utf-8')
        iv = key[0:16]
        en_text = aAESData
        cryptor = AES.new(key, AES.MODE_CBC, iv)
        plain_text = cryptor.decrypt(base64.b64decode(en_text))
        plain_text = bytes.decode(plain_text[:-plain_text[-1]])
        logging.info("aes decrypt data:" + plain_text)
        data_array = json.loads(plain_text)
        logging.info("json_load data:" + str(data_array))
        return data_array

    # vaas请求各个参数封装
    def request_api(self, aUrl):
        # 获取config中的key和token
        access_key = config.ACCESS_KEY
        access_token = config.ACCESS_TOKEN
        # 判断key和token是否有值
        if access_key == '' or access_token == '' or (len(access_key) != 12 and len(access_key) != 25):
            raise Exception("access_key或access_token格式错误")
        # 获取时间戳
        curTimeStamp = int(round(time.time() * 1000))
        # 获取参数
        textmessage = self.get_vaasparam()
        # AES加密参数
        aes_sec_mes = self.aes_encrypt(access_token, textmessage)
        # sha256签名
        sha256_sig = self.sha256_signature(aes_sec_mes, access_token, curTimeStamp)
        # 发送请求并解析
        return self.request_v2(access_token, aUrl, access_key, curTimeStamp, sha256_sig, aes_sec_mes)

    # 数据上报http请求
    def request_report(self, aUrl):
        # 获取完整url
        aUrl = self.report_url(aUrl)
        # 获取参数
        textmessage = self.get_reportparam()
        response = requests.request("POST", aUrl, data=textmessage)
        logging.info("response data is:" + response.text)
        resDic = json.loads(response.text)
        if resDic['code'] == 0 or resDic['code'] == '0':
            if 'data' in resDic:
                return resDic['msg']
        else:
            logging.fatal("request is fail")
            raise Exception(resDic['msg'])

    # 数据上报get url拼接
    def report_url(self, aUrl):
        curTimeStamp = int(time.time())
        access_key = config.ACCESS_KEY
        if access_key == '' or (len(access_key) != 12 and len(access_key) != 25):
            raise Exception("access_key格式错误")
        udid = self.udid
        md5_sig = self.md5_signature(curTimeStamp, access_key, udid)
        aUrl = aUrl % (curTimeStamp, access_key, udid, md5_sig)
        return aUrl

    # 数据上报md5加密
    def md5_signature(self, ts, access_key, udid):
        data = config.DATA_BEGION + str(ts) + access_key + udid + config.DATA_END
        md5_sign = hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()
        return md5_sign

    # vaas http请求
    def request_v2(self, aToken, aURL, aAccessKey, aTimestamp, aSignature, aAESData):
        payload = '{"access_key": "%s","params": "%s","sign": "%s","timestamp":%d}' % (
            aAccessKey, bytes.decode(aAESData), bytes.decode(aSignature), aTimestamp)
        logging.info("request data is:" + payload)
        headers = {"X-YL-KEY": aAccessKey, "X-YL-TIMESTAMP": str(aTimestamp)}
        response = requests.request("POST", aURL, data=payload, headers=headers)
        logging.info("response data is:" + response.text)
        # 解析返回值
        resDic = json.loads(response.text)
        if resDic['code'] == 200 or resDic['code'] == '200':
            if 'data' in resDic:
                return self.aes_decrypt(resDic['data'], aToken)
        else:
            logging.fatal("request is fail" + str(resDic))
            raise Exception(resDic['msg'])

    # vaas params拼接
    def get_vaasparam(self):
        # 公共入参
        defult = {'udid': self.udid, 'pkg_name': config.PKG_NAME, 'platform': config.PLATFORM}
        # 方法传参
        input = self.dict
        input.update(defult)
        params = json.dumps(input)
        return params

    # report params拼接
    def get_reportparam(self):
        # 公共入参
        defult = {"access_key": config.ACCESS_KEY,
                  "udid": self.udid,
                  "sn": int(round(time.time() * 1000))
                  }
        # 方法传参
        input = self.dict
        input.update(defult)
        params = json.dumps(input)
        return params
