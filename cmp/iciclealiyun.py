#-*- coding: utf-8 -*-
#ECS相关模块
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkcore.client import AcsClient
#阿里云处理异常相关模块
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
#RDS相关模块
from aliyunsdkrds.request.v20140815.DescribeDBInstancesRequest import DescribeDBInstancesRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstanceAttributeRequest import DescribeDBInstanceAttributeRequest
from aliyunsdkrds.request.v20140815.DescribeDBInstanceIPArrayListRequest import DescribeDBInstanceIPArrayListRequest
#账单相关模块
from aliyunsdkbssopenapi.request.v20171214.QueryInstanceBillRequest import QueryInstanceBillRequest
#NAT网关相关模块
from aliyunsdkecs.request.v20140526.DescribeForwardTableEntriesRequest import DescribeForwardTableEntriesRequest
from aliyunsdkecs.request.v20140526.DescribeNatGatewaysRequest import DescribeNatGatewaysRequest
#ssl证书相关模块
from aliyunsdkcore.request import CommonRequest
#WAF相关模块
from aliyunsdkwaf_openapi.request.v20190910.DescribeInstanceInfoRequest import DescribeInstanceInfoRequest
from aliyunsdkwaf_openapi.request.v20190910.DescribeDomainNamesRequest import DescribeDomainNamesRequest
from aliyunsdkwaf_openapi.request.v20190910.DescribeDomainAdvanceConfigsRequest import DescribeDomainAdvanceConfigsRequest
#CDN相关模块
from aliyunsdkcdn.request.v20180510.DescribeUserDomainsRequest import DescribeUserDomainsRequest
#OSS相关模块
from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest
from collections import OrderedDict 
#处理数据格式的模块
import json
import ast

"""
用来获取某个阿里云账号的ecs信息
"""
class IcicleAliyun():
    """
    操作阿里云的父类
    """
    def __init__(self, access_key_id, access_key_secret, region):
        """
        初始化阿里云相关的属性
        """
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region = region

    def connect(self):
        """
        连接阿里云账号
        """
        client = AcsClient(
        self.access_key_id,
        self.access_key_secret,
        self.region
        )
        return client

    def fetch_ecs_info(self):
        """
        获取所有ecs信息
        """
        client = self.connect()
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_PageSize(100)
        response_str = client.do_action_with_exception(request).decode("utf-8")
        response_dict =  json.loads(response_str)
        servers = response_dict['Instances']['Instance']
        return servers

    def fetch_rds_instances(self):
        """
        获取所有rds实例id
        """
        ins_list = []
        client = self.connect()
        request = DescribeDBInstancesRequest()
        request.set_accept_format('json')
        response_str = client.do_action_with_exception(request).decode("utf-8")
        response_dict =  json.loads(response_str)['Items']['DBInstance']
        for i in response_dict:
            ins_list.append(i['DBInstanceId'])
        return ins_list

    def fetch_rds_ins_ver(self):
        """
        获取rds实例的具体信息
        """
        client = self.connect()
        ins_ids = ','.join(self.fetch_rds_instances())
        request = DescribeDBInstanceAttributeRequest()
        request.set_accept_format('json')
        request.set_DBInstanceId(ins_ids)
        response = client.do_action_with_exception(request)
        response = json.loads(str(response, encoding='utf-8'))
        response = response['Items']['DBInstanceAttribute']
        return response

    def fetch_whitelist(self, instance_id):
        """
        获取rds实例的白名单
        """
        client = self.connect()
        request = DescribeDBInstanceIPArrayListRequest()
        request.set_accept_format('json')
        request.set_DBInstanceId(instance_id)

        response = client.do_action_with_exception(request)
        response = json.loads(str(response, encoding='utf-8'))
        return response

    def fetch_price(self, last_month):
        """
        获取该账号下所有实例的费用
        """
        client = self.connect()
        request = QueryInstanceBillRequest()
        request.set_accept_format('json')
        request.set_BillingCycle(last_month)
        request.set_PageSize(300)
        response = client.do_action_with_exception(request)
        response = str(response, encoding='utf-8')
        response = json.loads(response)
        bill_list = response['Data']['Items']['Item']
        return bill_list
    
    def fetch_dnat_ftable(self):
        """
        返回dnat的forward table id
        """
        client = self.connect()
        request = DescribeNatGatewaysRequest()
        request.set_accept_format('json')
        response = client.do_action_with_exception(request).decode("utf-8")
        response_dict =  json.loads(response)
        fTableId = response_dict['NatGateways']['NatGateway'][0]['ForwardTableIds']['ForwardTableId'][0]
        return fTableId

    def fetch_dnat_entries(self):
        """
        获取该转发表下的所有dnat条目
        """
        client = self.connect()
        request = DescribeForwardTableEntriesRequest()
        request.set_accept_format('json')
        TableId = self.fetch_dnat_ftable()
        request.set_ForwardTableId(TableId)
        request.set_PageSize(50)
        response = client.do_action_with_exception(request)
        response = str(response, encoding='utf-8')
        response = json.loads(response)
        entries = response['ForwardTableEntries']['ForwardTableEntry']
        return entries

    def fetch_cert(self):
        """
        获取ssl证书信息
        """
        client = self.connect()
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('cas.aliyuncs.com')
        request.set_method('POST')
        request.set_version('2018-07-13')
        request.set_action_name('DescribeUserCertificateList')
        request.add_query_param('ShowSize', "50")
        request.add_query_param('CurrentPage', "1")
        response = client.do_action(request)
        response = str(response, encoding = 'utf-8')
        response = json.loads(response)
        return response

    def fetch_waf(self):
        """
        获取waf相关信息，返回域名详细信息列表
        """
        client = self.connect()
        request = DescribeInstanceInfoRequest()
        request.set_accept_format('json')
        response = client.do_action_with_exception(request)
        response = str(response, encoding='utf-8')
        ins_id = json.loads(response)['InstanceInfo']['InstanceId']

        request = DescribeDomainNamesRequest()
        request.set_accept_format('json')
        request.set_InstanceId(ins_id)
        response = client.do_action_with_exception(request)
        response = str(response, encoding='utf-8')
        dn_list = json.loads(response)['DomainNames']
        
        request = DescribeDomainAdvanceConfigsRequest()
        request.set_accept_format('json')
        request.set_InstanceId(ins_id)
        request.set_DomainList(",".join(dn_list))
        response = client.do_action_with_exception(request)
        response = str(response, encoding='utf-8')
        response = json.loads(response)['DomainConfigs']
        return response

    def fetch_cdn(self):
        """
        返回包含cdn信息的列表
        """
        client = self.connect()
        request = DescribeUserDomainsRequest()
        request.set_accept_format('json')
        request.set_PageSize(100)
        response = client.do_action_with_exception(request)
        response = json.loads(str(response, encoding='utf-8'))
        r_list = response['Domains']['PageData']
        return r_list
   
class OssInfo(IcicleAliyun):
    """操作oss的子类"""
    def __init__(self, access_key_id, access_key_secret, region, start_time, end_time):
        super().__init__(access_key_id, access_key_secret, region)
        self.start_time = start_time
        self.end_time = end_time

    def fetch_bucket_usage(self):
        """
        返回该账号下的所有bucket容量信息的列表。
        获取bucket容量方法：
        使用reversed方法倒序遍历列表，把各种存储类型的使用量相加，每种存储类型只能加一次
        最终得到一个bucket的总容量/使用量
        """
        client = self.connect()
        request = DescribeMetricListRequest()
        request.set_accept_format('json')
        request.set_Namespace("acs_oss")
        request.set_MetricName("MeteringStorageUtilization")
        response = client.do_action_with_exception(request)
        list = ast.literal_eval(json.loads(str(response, encoding='utf-8'))['Datapoints'])
        return list

    def fetch_total_req(self):
        """
        返回所有bucket当月请求数的列表。
        获取当月请求数方法：
        把列表中特定BucketName的每个字典的TotalRequestCount键对应值相加得到当月所有请求数
        """
        client = self.connect()
        request = DescribeMetricListRequest()
        request.set_accept_format('json')
        request.set_Namespace("acs_oss")
        #request.set_StartTime('%s-%s-01 00:00:00' % (year, month))
        request.set_StartTime('%s 00:00:00' % self.start_time)
        #request.set_EndTime('%s 23:59:59' % today)
        request.set_EndTime('%s 23:59:59' % self.end_time)
        request.set_MetricName("TotalRequestCount")
        response = client.do_action_with_exception(request)
        list = ast.literal_eval(json.loads(str(response, encoding='utf-8'))['Datapoints'])
        return list

    def fetch_traffic_recv(self):
        """
        返回当月bucket的入方向公网流量
        获取某个bucket入方向流量的方法：
        筛选该bucket的InternetRecv键对应的值并求和
        """
        client = self.connect()
        request = DescribeMetricListRequest()
        request.set_accept_format('json')
        request.set_Namespace("acs_oss")
        #request.set_StartTime('%s-%s-01 00:00:00' % (year, month))
        request.set_StartTime('%s 00:00:00' % self.start_time)
        #request.set_EndTime('%s 23:59:59' % today)
        request.set_EndTime('%s 23:59:59' % self.end_time)
        request.set_MetricName("InternetRecv")
        response = client.do_action_with_exception(request)
        list = ast.literal_eval(json.loads(str(response, encoding='utf-8'))['Datapoints'])
        return list

    def fetch_traffic_send(self):
        """
        返回当月bucket的出方向公网流量
        获取某个bucket入方向流量的方法：
        筛选该bucket的InternetSend键对应的值并求和
        """
        client = self.connect()
        request = DescribeMetricListRequest()
        request.set_accept_format('json')
        request.set_Namespace("acs_oss")
        #request.set_StartTime('%s-%s-01 00:00:00' % (year, month))
        request.set_StartTime('%s 00:00:00' % self.start_time)
        #request.set_EndTime('%s 23:59:59' % today)
        request.set_EndTime('%s 23:59:59' % self.end_time)
        request.set_MetricName("InternetSend")
        response = client.do_action_with_exception(request)
        list = ast.literal_eval(json.loads(str(response, encoding='utf-8'))['Datapoints'])
        return list


class MonthData(OssInfo):
    """
    以html表格形式生成oss月份数据
    """
    def __init__(self, access_key_id, access_key_secret, region, start_time, end_time):
        super().__init__(access_key_id, access_key_secret, region, start_time, end_time)

    def get_buc_name_usage(self):
        usage_list1 = self.fetch_bucket_usage()
        self.buc_name1 = []
        buc_dict1 = OrderedDict()
        for i in usage_list1:
            if i['BucketName'] not in self.buc_name1 and i['MeteringStorageUtilization'] != 0:
                self.buc_name1.append(i['BucketName'])
        for i in self.buc_name1:
            storage_type1 = []
            buc_dict1[i] = 0
            for j in reversed(usage_list1):
                if j['BucketName'] == i and j['storageType'] not in storage_type1:
                    storage_type1.append(j['storageType'])
                    buc_dict1[i] += j['MeteringStorageUtilization']
        for k, v in buc_dict1.items():
            l = len(str(int(v)))
            if l >= 13:
                v = v / 1024 / 1024 / 1024 / 1024
                v = str(int(v)) + 'TB'
            elif l >= 10 and l < 13:
                v = v / 1024 / 1024 / 1024
                v = str(int(v)) + 'GB'
            elif l >= 7 and l < 10:
                v = v / 1024 / 1024
                v = str(int(v)) + 'MB'
            elif l < 7:
                v = v / 1024
                v = str(int(v)) + 'KB'
            buc_dict1[k] = v
        usage_list2 = [v for i in self.buc_name1 for k, v in buc_dict1.items() if k == i]
        return [self.buc_name1, usage_list2]

    def get_req(self):
        req_list1 = self.fetch_total_req()
        req_dict1 = OrderedDict()
        for i in req_list1:
            try:
                req_dict1[i['BucketName']] += i['TotalRequestCount']
            except:
                req_dict1[i['BucketName']] = i['TotalRequestCount']
        req_list2 = [v for i in self.buc_name1 for k, v in req_dict1.items() if k == i]
        return req_list2

    def get_recv(self):
        recv_list1 = self.fetch_traffic_recv()
        recv_dict1 = OrderedDict()
        for i in recv_list1:
            try:
                recv_dict1[i['BucketName']] += i['InternetRecv']
            except:
                recv_dict1[i['BucketName']] = i['InternetRecv']
        for k, v in recv_dict1.items():
            l = len(str(int(v)))
            if l >= 13:
                v = v / 1024 / 1024 / 1024 / 1024
                v = str(int(v)) + 'TB'
            elif l >= 10 and l < 13:
                v = v / 1024 / 1024 / 1024
                v = str(int(v)) + 'GB'
            elif l >= 7 and l < 10:
                v = v / 1024 / 1024
                v = str(int(v)) + 'MB'
            elif l < 7:
                v = v / 1024
                v = str(int(v)) + 'KB'
            recv_dict1[k] = v
        recv_list2 = [v for i in self.buc_name1 for k, v in recv_dict1.items() if k == i]
        return recv_list2

    def get_send(self):
        send_list1 = self.fetch_traffic_send()
        send_dict1 = OrderedDict()
        for i in send_list1:
            try:
                send_dict1[i['BucketName']] += i['InternetSend']
            except:
                send_dict1[i['BucketName']] = i['InternetSend']
        for k, v in send_dict1.items():
            l = len(str(int(v)))
            if l >= 13:
                v = v / 1024 / 1024 / 1024 / 1024
                v = str(int(v)) + 'TB'
            elif l >= 10 and l < 13:
                v = v / 1024 / 1024 / 1024
                v = str(int(v)) + 'GB'
            elif l >= 7 and l < 10:
                v = v / 1024 / 1024
                v = str(int(v)) + 'MB'
            elif l < 7:
                v = v / 1024
                v = str(int(v)) + 'KB'
            send_dict1[k] = v
        send_list2 = [v for i in self.buc_name1 for k, v in send_dict1.items() if k == i]
        return send_list2

