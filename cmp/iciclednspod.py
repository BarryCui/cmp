#-*- coding: utf-8 -*-
from urllib import request, parse
import json
import os

class IcicleDnsPod():
    """
    调用dnspod的父类
    """
    def __init__(self, login_token):
        self.login_token = login_token

    def get_dns_list(self):
        #获取dns列表
        data = parse.urlencode({"login_token": self.login_token,\
                                "format": "json"}).encode()
        req =  request.Request("https://dnsapi.cn/Domain.List", data=data) # this will make the method "POST"
        resp = request.urlopen(req)
        raw_data = resp.read()
        json_data = json.loads(raw_data.decode('utf-8'))
        list_data = json_data['domains']
        return list_data
    
    def get_record_raw(self, id):
        #获取记录的原始数据
        data = parse.urlencode({"login_token": self.login_token,\
                                "format": "json", "domain_id": id}).encode()
        req =  request.Request("https://dnsapi.cn/Record.List", data=data) # this will make the method "POST"
        resp = request.urlopen(req)
        raw_data = resp.read()
        json_data = json.loads(raw_data.decode('utf-8'))
        return json_data

    def get_record_list(self):
        #获取每个dns域名对应的记录列表
        dns_list = self.get_dns_list()
        id_list = [i['id'] for i in dns_list]
        r_list = [self.get_record_raw(i) for i in id_list]
        return r_list







