#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import subprocess
import json
import os
from dotenv import load_dotenv
#
#Azure cli set up:
#######################################################################
#sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
#
#sudo sh -c 'echo -e "[azure-cli]
#name=Azure CLI
#baseurl=https://packages.microsoft.com/yumrepos/azure-cli
#enabled=1
#gpgcheck=1
#gpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo'
#
#sudo yum install azure-cli
#######################################################################
#az cloud set --name AzureChinaCloud
#az login
#######################################################################
#Usage:
#az vm list
#Show details of a vm based on its name
#az vm show --resource-group example-group-name --name example-vm-name
#
#
#
#
#
class IcicleAzure():
    
    def login(self):
        if os.path.exists('/cmp/env/.env'):
            load_dotenv(dotenv_path='/cmp/env/.env') # load environment variables
        elif os.path.exists('/home/vagrant/cmp/cmp/env/.env'):
            load_dotenv(dotenv_path='/home/vagrant/cmp/cmp/env/.env') # load environment variables
        APP_ID = os.getenv("APP_ID")
        PASSWORD = os.getenv("PASSWORD")
        TENANT_ID = os.getenv("TENANT_ID")
        APP_URL = os.getenv("APP_URL")
        cmd_set_region = ['az', 'cloud', 'set', '-n', 'AzureChinaCloud'] # Alter Azure region to China
        cmd_login = ['az', 'login', '--service-principal', '-u', APP_URL, '--username', APP_ID, '--password', PASSWORD, '--tenant', TENANT_ID] # Login Azure via service principal
        try:
            subprocess.run(cmd_set_region)
        except:
            pass
        else:
            subprocess.run(cmd_login)
        
    def getDbList(self):
        self.login()
        resource_group = os.getenv("RESOURCE_GROUP")
        db_server = os.getenv("SQL_SERVER_NAME")
        cmd_db_list = 'az sql db list --resource-group %s --server %s --query [].name' % (resource_group, db_server)
        output_name = subprocess.check_output(cmd_db_list, shell=True, universal_newlines=True) #Get raw output from azure cli
        output_name_list = json.loads(output_name) #Turn into a standard dictionary format
        db_list = [] #db detail list
        db_format_list = [] #Formatted db list
        for i in output_name_list:
            cmd_db_show = 'az sql db show --resource-group %s --server %s --name %s' % (resource_group, db_server, i)
            cmd_db_list_usage = 'az sql db list-usages --resource-group %s --server %s --name %s' % (resource_group, db_server, i)
            db_info = subprocess.check_output(cmd_db_show, shell=True, universal_newlines=True)
            db_info = json.loads(db_info)
            db_size = subprocess.check_output(cmd_db_list_usage, shell=True, universal_newlines=True)
            db_size = json.loads(db_size)[-1]['currentValue']
            db_info['usedBytes'] = int(db_size)
            db_list.append(db_info)

        for i in db_list:
            res_dict = {}
            res_dict['name'] = i['name']
            res_dict['creationDate'] = i['creationDate']
            res_dict['resourceGroup'] = i['resourceGroup']
            res_dict['location'] = i['location']
            res_dict['collation'] = i['collation']
            res_dict['usedBytes'] = i['usedBytes']
            res_dict['maxSizeBytes'] = i['maxSizeBytes']
            res_dict['status'] = i['status']
            res_dict['earliestRestoreDate']  = i['earliestRestoreDate'] 
            res_dict['type'] = i['type']
            res_dict['tier'] = i['currentSku']['tier'] + ' ' + i['currentServiceObjectiveName'] + ': ' + str(i['currentSku']['capacity']) + 'DTU'
            db_format_list.append(res_dict)   
        return db_format_list

    def getVmList(self): 
        self.login()
        resource_group = os.getenv("RESOURCE_GROUP")
        output = subprocess.check_output("az vm list", shell=True, universal_newlines=True) #Get raw output from azure cli
        output = json.loads(output) #Turn into a standard dictionary format
        vm_names = [i['name'] for i in output] #Get a list of vm host names
        #Produce a list of dictionaries of vm host details
        vm_de_list = [] #For storing vm details raw data
        vm_de_format_list = [] #Formatted vm detail data
        for i in vm_names:
            cmd_vm_show = 'az vm show --resource-group %s -d --name %s' % (resource_group, i)
            detail = subprocess.check_output(cmd_vm_show, shell=True, universal_newlines=True)
            detail = json.loads(detail)
            vm_de_list.append(detail)

        for i in vm_de_list:
            res_dict = {}
            res_dict['name'] = i['name']
            res_dict['hardwareProfile'] = i['hardwareProfile']
            res_dict['id'] = i['id']
            res_dict['resourceGroup'] = i['resourceGroup']
            res_dict['location'] = i['location']
            res_dict['DataDiskSizeGb'] = i['storageProfile']['dataDisks'][0]['diskSizeGb']
            res_dict['image'] = i['storageProfile']['imageReference']['offer'] + ' ' + i['storageProfile']['imageReference']['sku']
            res_dict['OsDiskSizeGb'] = i['storageProfile']['osDisk']['diskSizeGb']
            res_dict['privateIps'] = i['privateIps']
            res_dict['publicIps'] = i['publicIps']
            vm_de_format_list.append(res_dict)   
        return vm_de_format_list
