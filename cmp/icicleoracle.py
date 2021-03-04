#-*- coding: utf-8 -*-
import oci
import json, os
from dotenv import load_dotenv

'''
通过Oracle Cloud API收集vm信息。

API的依赖关系如下：
通过list_instances获取vm的大部分信息，
通过list_vnic_attachments，使用上一步的instance_id获取vnic_id，
通过get_vnic获取ip信息。
'''
class IcicleOracle():
    def setConfig(self, region):
        """
        设置配置
        """
        load_dotenv()
        user_ocid = os.getenv("OC_USER_OCID")
        key_file = os.getenv("OC_KEY_FILE")
        fingerprint = os.getenv("OC_FINGERPRINT")
        tenancy = os.getenv("OC_TENANCY")
        config = {
        "user": user_ocid,
        "key_file": key_file,
        "fingerprint": fingerprint,
        "tenancy": tenancy,
        "region": region
        }
        try:
            oci.config.validate_config(config)
        except Exception as e:
            return e
        else:
            return config

    def makeConfList(self):
        """
        不同区域的配置的列表
        """
        config_frankfurt = self.setConfig(os.getenv("OC_REGION_1"))
        config_korea = self.setConfig(os.getenv("OC_REGION_2"))
        config_us = self.setConfig(os.getenv("OC_REGION_3"))
        conf_list = []
        conf_list.append(config_frankfurt)
        conf_list.append(config_korea)
        conf_list.append(config_us)
        return conf_list

    def getInsListRaw(self, config):
        """
        获取实例列表，数据格式需要进一步处理
        """
        core_client = oci.core.ComputeClient(config)
        list_instances_response = core_client.list_instances(os.getenv("OC_TENANCY"))
        response = list_instances_response.data
        return response

    def getInsList(self):
        """
        生成处理过后的实例列表
        """
        config_list = self.makeConfList()
        ins_list = []
        for i in config_list:
            ins_list_raw = self.getInsListRaw(i)
            for j in ins_list_raw:
                ins_list.append(json.loads(str(j)))
        return ins_list

    def getVnicRaw(self, config):
        """
        获取网卡数据列表，数据格式需要进一步处理
        """
        core_client = oci.core.ComputeClient(config)
        list_vnic_attachments_response = core_client.list_vnic_attachments(os.getenv("OC_TENANCY"))
        response = list_vnic_attachments_response.data
        return response

    def getVnicList(self):
        """
        生成处理过后的网卡数据列表
        """
        config_list = self.makeConfList()
        vnic_list = []
        for i in config_list:
            vnic_list_raw = self.getVnicRaw(i)
            for j in vnic_list_raw:
                vnic_list.append(json.loads(str(j)))
        return vnic_list

    def getVnicIp(self):
        """
        生成ip列表
        """
        config_list = self.makeConfList()   
        get_vnic_ip_list = []
        vnic_list_all = self.getVnicList()
        for i in config_list:
            core_client = oci.core.VirtualNetworkClient(i)
            for j in vnic_list_all:
                try:
                    get_vnic_response = core_client.get_vnic(j['vnic_id'])
                except:
                    pass
                else:
                    get_vnic_response = json.loads(str(get_vnic_response.data))
                    get_vnic_ip_list.append(get_vnic_response)
        return get_vnic_ip_list

    def makeVmList(self):
        """
        生成最终的vm列表
        """
        ins_list = self.getInsList()
        ip_list = self.getVnicIp()  
        vnic_list = self.getVnicList() 
        final_list = []
        for i in ins_list:
            final_dict = {}
            for j in vnic_list:
                if j['instance_id'] == i['id']:
                    for k in ip_list:
                        if k['id'] == j['vnic_id']:
                            final_dict['private_ip'] = k['private_ip']
                            final_dict['public_ip'] = k['public_ip']
                            final_dict['display_name'] = i['display_name']
                            final_dict['availability_domain'] = i['availability_domain']
                            final_dict['lifecycle_state'] = i['lifecycle_state']
                            final_dict['shape'] = i['shape']
                            final_dict['memory'] = i['shape_config']['memory_in_gbs']
                            final_dict['bandwidth'] = i['shape_config']['networking_bandwidth_in_gbps']
                            final_dict['cpus'] = i['shape_config']['ocpus']
                            final_dict['processor_description'] = i['shape_config']['processor_description']
                            final_dict['time_created'] = i['time_created']
            final_list.append(final_dict)      
        return final_list           
    




