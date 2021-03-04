#-*- coding: utf-8 -*-

import click
from cmp import app, db
from cmp.models import *
from cmp.iciclealiyun import IcicleAliyun, MonthData
from cmp.icicleoracle import IcicleOracle
from cmp.icicleazure import IcicleAzure
from cmp.iciclednspod import IcicleDnsPod
import json
import datetime
from calendar import monthrange
import os
from dotenv import load_dotenv

@app.cli.command()
def generate():
    """
    生成云平台资产信息.
    """ 
    click.echo("Initializing database...")
    db.drop_all() # drop all tables
    db.create_all() # create all tables
    click.echo("Database initialized.")
    click.echo("Start generating data...")
    if os.path.exists('/cmp/env/.env'):
        load_dotenv(dotenv_path='/cmp/env/.env') # load environment variables
    elif os.path.exists('/home/vagrant/cmp/cmp/env/.env'):
        load_dotenv(dotenv_path='/home/vagrant/cmp/cmp/env/.env') # load environment variables
    now = datetime.datetime.now().isoformat() # get the current time
    last_m = (datetime.datetime.today() - datetime.timedelta(30)).strftime("%Y-%m") # last month
    # aliyun user1 settings
    user1_akid = os.getenv('user1_AccessKeyId')
    user1_aksecret = os.getenv('user1_AccessKeySecret')
    user1_region = os.getenv('user1_RegionId')
    user1_region2 = os.getenv('user1_RegionId2')
    user1_AccountName = os.getenv('user1_AccountName')
    # aliyun user2 settings
    user2_akid = os.getenv('user2_AccessKeyId')
    user2_aksecret = os.getenv('user2_AccessKeySecret')
    user2_region = os.getenv('user2_RegionId')
    user2_region2 = os.getenv('user2_RegionId2')
    user2_AccountName = os.getenv('user2_AccountName')

    #### ECS ####   
    user1_cloud_obj = IcicleAliyun(user1_akid, user1_aksecret, user1_region) # get access to aliyun api
    user1_cloud_servers = user1_cloud_obj.fetch_ecs_info() # fetch ecs data
    user1_cloud_prices = user1_cloud_obj.fetch_price(last_m) # fetch price data of the last month 
    user1_cloud_price_dict = {} # store price data in <instanceid:price> format

    user2_cloud_obj = IcicleAliyun(user2_akid, user2_aksecret, user2_region) 
    user2_cloud_servers = user2_cloud_obj.fetch_ecs_info() 
    user2_cloud_prices = user2_cloud_obj.fetch_price(last_m)
    user2_cloud_price_dict = {}
    # user1 data processing
    # format price data into a dict
    for i in user1_cloud_prices:
        try:
            user1_cloud_price_dict[i['InstanceID']] += i['PaymentAmount']
        except:
            user1_cloud_price_dict[i['InstanceID']] = i['PaymentAmount']
    # obtain value of each column
    for i in user1_cloud_servers:
        InstanceId = i['InstanceId']
        InstanceName = i['InstanceName']
        ZoneId = i['ZoneId']
        RegionId = i['RegionId']
        InstanceType = i['InstanceType']
        PrivateIp = i['NetworkInterfaces']['NetworkInterface'][0]['PrimaryIpAddress']
        PublicIP = i['EipAddress']['IpAddress']
        Memory = str(i['Memory'])
        Cpu = str(i['Cpu'])
        OSName = i['OSName']
        CreationTime = i['CreationTime']
        MonthPrice = ""
        try:
            if InstanceId in user1_cloud_price_dict.keys():
                MonthPrice = str(user1_cloud_price_dict[InstanceId])
        except Exception as e:
            MonthPrice = "Null"
        # instantiate ecs table class
        row = AliyunVm(InstanceId=InstanceId, InstanceName=InstanceName, ZoneId=ZoneId, \
                RegionId=RegionId, AccountName=user1_AccountName, InstanceType=InstanceType, \
                PrivateIp=PrivateIp, PublicIP=PublicIP, Memory=Memory, Cpu=Cpu, \
                OSName=OSName, CreationTime=CreationTime, MonthPrice=MonthPrice)
        db.session.add(row) # add a row to the db session
    # user2 data processing
    for i in user2_cloud_prices:
        try:
            user2_cloud_price_dict[i['InstanceID']] += i['PaymentAmount']
        except:
            user2_cloud_price_dict[i['InstanceID']] = i['PaymentAmount']
    
    for i in user2_cloud_servers:
        InstanceId = i['InstanceId']
        InstanceName = i['InstanceName']
        ZoneId = i['ZoneId']
        RegionId = i['RegionId']
        InstanceType = i['InstanceType']
        PrivateIp = i['NetworkInterfaces']['NetworkInterface'][0]['PrimaryIpAddress']
        PublicIP = i['EipAddress']['IpAddress']
        Memory = str(i['Memory'])
        Cpu = str(i['Cpu'])
        OSName = i['OSName']
        CreationTime = i['CreationTime']
        MonthPrice = ""
        try:
            if InstanceId in user2_cloud_price_dict.keys():
                MonthPrice = str(user2_cloud_price_dict[InstanceId])
        except Exception as e:
            MonthPrice = "Null"

        row = AliyunVm(InstanceId=InstanceId, InstanceName=InstanceName, ZoneId=ZoneId, \
                RegionId=RegionId, AccountName=user2_AccountName, InstanceType=InstanceType, \
                PrivateIp=PrivateIp, PublicIP=PublicIP, Memory=Memory, Cpu=Cpu, \
                OSName=OSName, CreationTime=CreationTime, MonthPrice=MonthPrice)
        db.session.add(row)
    
    db.session.commit() # commit the changes to the db 
    #### RDS ####
    user1_cloud_rdses = user1_cloud_obj.fetch_rds_ins_ver()
    user2_cloud_rdses = user2_cloud_obj.fetch_rds_ins_ver()
    for i in user1_cloud_rdses:
        DBInstanceId = i['DBInstanceId']
        ConnectionString = i['ConnectionString']
        ZoneId = i['ZoneId']
        RegionId = i['RegionId']
        Port = i['Port']
        DBInstanceClass = i['DBInstanceClass']
        DBInstanceCPU = i['DBInstanceCPU']
        DBInstanceMemory = str(i['DBInstanceMemory'])
        DBInstanceStorage = i['DBInstanceStorage']
        CreationTime = i['CreationTime']
        ExpireTime = i['ExpireTime']
        Engine = i['Engine']
        SecurityIPList = i['SecurityIPList']
        MonthPrice = ""
        try:
            MonthPrice = str(user1_cloud_price_dict[DBInstanceId])
        except:
            MonthPrice = ""
        try:
            DBInstanceDescription = i['DBInstanceDescription']
        except:
            DBInstanceDescription = DBInstanceId

        row = AliyunRds(DBInstanceId=DBInstanceId, ConnectionString=ConnectionString,\
                        AccountName=user1_AccountName, ZoneId=ZoneId, RegionId=RegionId,\
                        Port=Port, DBInstanceDescription=DBInstanceDescription, DBInstanceClass=DBInstanceClass,\
                        DBInstanceCPU=DBInstanceCPU, DBInstanceMemory=DBInstanceMemory, DBInstanceStorage=DBInstanceStorage,\
                        CreationTime=CreationTime, ExpireTime=ExpireTime, Engine=Engine, SecurityIPList=SecurityIPList,\
                        MonthPrice=MonthPrice)
        db.session.add(row)
 
    for i in user2_cloud_rdses:
        DBInstanceId = i['DBInstanceId']
        ConnectionString = i['ConnectionString']
        ZoneId = i['ZoneId']
        RegionId = i['RegionId']
        Port = i['Port']
        DBInstanceClass = i['DBInstanceClass']
        DBInstanceCPU = i['DBInstanceCPU']
        DBInstanceMemory = str(i['DBInstanceMemory'])
        DBInstanceStorage = i['DBInstanceStorage']
        CreationTime = i['CreationTime']
        ExpireTime = i['ExpireTime']
        Engine = i['Engine']
        SecurityIPList = i['SecurityIPList']
        MonthPrice = ""
        try:
            MonthPrice = str(user2_cloud_price_dict[DBInstanceId])
        except:
            MonthPrice = ""
        try:
            DBInstanceDescription = i['DBInstanceDescription']
        except:
            DBInstanceDescription = DBInstanceId
        row = AliyunRds(DBInstanceId=DBInstanceId, ConnectionString=ConnectionString,\
                        AccountName=user2_AccountName, ZoneId=ZoneId, RegionId=RegionId,\
                        Port=Port, DBInstanceDescription=DBInstanceDescription, DBInstanceClass=DBInstanceClass,\
                        DBInstanceCPU=DBInstanceCPU, DBInstanceMemory=DBInstanceMemory, DBInstanceStorage=DBInstanceStorage,\
                        CreationTime=CreationTime, ExpireTime=ExpireTime, Engine=Engine, SecurityIPList=SecurityIPList,\
                        MonthPrice=MonthPrice)
        db.session.add(row)     
    
    db.session.commit() # commit the changes to the db 
    #### Dnat ####
    # fetch dnat list
    user1_dnat_list = user1_cloud_obj.fetch_dnat_entries()
    user2_dnat_list = user2_cloud_obj.fetch_dnat_entries()
    # insert into db
    for i in user1_dnat_list:
        ExternalPort = i['ExternalPort']
        ExternalIp = i['ExternalIp']
        InternalPort = i['InternalPort']
        InternalIp = i['InternalIp']
        row = AliyunDnat(ExternalPort=ExternalPort, ExternalIp=ExternalIp, InternalPort=InternalPort, InternalIp=InternalIp)
        db.session.add(row)
    
    for i in user2_dnat_list:
        ExternalPort = i['ExternalPort']
        ExternalIp = i['ExternalIp']
        InternalPort = i['InternalPort']
        InternalIp = i['InternalIp']
        row = AliyunDnat(ExternalPort=ExternalPort, ExternalIp=ExternalIp, InternalPort=InternalPort, InternalIp=InternalIp)
        db.session.add(row)

    db.session.commit() # commit the changes to the db 
    #### Cdn ####
    user1_cdn = user1_cloud_obj.fetch_cdn()
    for i in user1_cdn:
        DomainName = i['DomainName']
        Cname = i['Cname']
        CreationTime = i['GmtCreated']
        Coverage = i['Coverage']
        OriginAddress = i['Sources']['Source'][0]['Content']
        row = AliyunCdn(DomainName=DomainName, Cname=Cname, CreationTime=CreationTime,
                    Coverage=Coverage, OriginAddress=OriginAddress)
        db.session.add(row)

    db.session.commit() # commit the changes to the db 
    #### Waf ####
    user1_cloud_obj2 = IcicleAliyun(user1_akid, user1_aksecret, user1_region2) # waf needs the region to be cn-shangzhou
    user1_waf = user1_cloud_obj2.fetch_waf()
    for i in user1_waf:
        DomainName = i['Domain']
        OriginAddress = ','.join(i['Profile']['Rs'])
        HttpPort = ','.join([str(j) for j in i['Profile']['HttpPort']])
        HttpsPort = ','.join([str(j) for j in i['Profile']['HttpsPort']])
        Cname = i['Profile']['Cname']
        AccountName = user1_AccountName
        row = AliyunWaf(DomainName=DomainName, OriginAddress=OriginAddress, HttpPort=HttpPort,
        HttpsPort=HttpsPort, Cname=Cname, AccountName=AccountName)
        db.session.add(row)

    user2_cloud_obj2 = IcicleAliyun(user2_akid, user2_aksecret, user2_region2) # waf needs the region to be cn-shangzhou
    user2_waf = user2_cloud_obj2.fetch_waf()
    for i in user2_waf:
        DomainName = i['Domain']
        OriginAddress = ','.join(i['Profile']['Rs'])
        HttpPort = ','.join([str(j) for j in i['Profile']['HttpPort']])
        HttpsPort = ','.join([str(j) for j in i['Profile']['HttpsPort']])
        Cname = i['Profile']['Cname']
        AccountName = user1_AccountName
        row = AliyunWaf(DomainName=DomainName, OriginAddress=OriginAddress, HttpPort=HttpPort,
        HttpsPort=HttpsPort, Cname=Cname, AccountName=AccountName)
        db.session.add(row)

    db.session.commit() # commit the changes to the db 
    #### Ssl ####
    user1_cert= user1_cloud_obj.fetch_cert()['CertificateList']
    for i in user1_cert:
        CertName = i['name']
        CertId = i['id']
        DomainName = i['sans']
        Issuer = i['issuer']
        StartDate = i['startDate']
        EndDate = i['endDate']
        AccountName = user1_AccountName
        row = AliyunSsl(CertName=CertName, CertId=CertId, DomainName=DomainName, Issuer=Issuer,
        StartDate=StartDate, EndDate=EndDate, AccountName=AccountName)
        db.session.add(row)

    user2_cert= user2_cloud_obj.fetch_cert()['CertificateList']
    for i in user2_cert:
        CertName = i['name']
        CertId = i['id']
        DomainName = i['sans']
        Issuer = i['issuer']
        StartDate = i['startDate']
        EndDate = i['endDate']
        AccountName = user2_AccountName
        row = AliyunSsl(CertName=CertName, CertId=CertId, DomainName=DomainName, Issuer=Issuer,
        StartDate=StartDate, EndDate=EndDate, AccountName=AccountName)
        db.session.add(row)

    db.session.commit() # commit the changes to the db 
    #### Oss ####
    #当前时间
    today = datetime.date.today()
    year = today.year
    month = today.month
    this_start = '%s-%s-01' % (year, month)
    this_end = '%s' % today
    #上月时间
    if (month - 1) > 0:
        last_month = month - 1
    else:
        last_month = 12
        year = year - 1
    last_day = monthrange(year, last_month)[1]
    last_start = '%s-%s-01' % (year, last_month)
    last_end = '%s-%s-%s' % (year, last_month, last_day)
    
    #创建获取数据的实例
    user1_data_this_month = MonthData(user1_akid, user1_aksecret, user1_region, this_start, this_end)
    user1_data_last_month = MonthData(user1_akid, user1_aksecret, user1_region, last_start, last_end)
    #设置变量
    BucketName = user1_data_this_month.get_buc_name_usage()[0]
    VolThisMon = user1_data_this_month.get_buc_name_usage()[1]
    VolLastMon = user1_data_last_month.get_buc_name_usage()[1]
    ReqThisMon = user1_data_this_month.get_req()
    ReqLastMon = user1_data_last_month.get_req()
    RecvThisMon = user1_data_this_month.get_recv()
    RecvLastMon = user1_data_last_month.get_recv()
    SendThisMon = user1_data_this_month.get_send()
    SendLastMon = user1_data_last_month.get_send()
    
    for co1,co2,co3,co4,co5,co6,co7,co8,co9 in zip(BucketName, VolThisMon, VolLastMon,
                                                   ReqThisMon, ReqLastMon,
                                                   RecvThisMon, RecvLastMon,
                                                   SendThisMon, SendLastMon):   
        row = AliyunOss(BucketName=co1,VolThisMon=co2,VolLastMon=co3,
                        ReqThisMon=co4,ReqLastMon=co5,
                        RecvThisMon=co6,RecvLastMon=co7,
                        SendThisMon=co8,SendLastMon=co9)
        db.session.add(row)

    db.session.commit() # commit the changes to the db 
    #### Oracle Cloud Vm ####
    oc_obj = IcicleOracle()
    oc_vm_list = oc_obj.makeVmList()
    for i in oc_vm_list:
        row = OcVm(Name=i['display_name'], PrivateIp=i['private_ip'], PublicIp=i['public_ip'],
                   Zone=i['availability_domain'], State=i['lifecycle_state'], Shape=i['shape'], 
                   NumOfCpu=i['cpus'], CpuDesc=i['processor_description'], Memory=i['memory'],
                   Bandwidth=i['bandwidth'], CreatedOn=i['time_created'])
        db.session.add(row)

    db.session.commit() # commit the changes to the db 
    #### Azure ####
    az_obj = IcicleAzure()
    # vm
    az_vms = az_obj.getVmList()
    for i in az_vms:
        row = AzVm(Name=i['name'], PrivateIp=i['privateIps'], PublicIp=i['publicIps'],
                   HardwareProfile=i['hardwareProfile']['vmSize'], ResourceGroup=i['resourceGroup'],
                   Location=i['location'], OsDiskSizeGb=i['OsDiskSizeGb'],
                   DataDiskSizeGb=i['DataDiskSizeGb'], Image=i['image'])
        db.session.add(row)
    db.session.commit() # commit the changes to the db 
    # db
    az_dbs = az_obj.getDbList()
    for i in az_dbs:
        row = AzDb(Name=i['name'], CreationDate=i['creationDate'], ResourceGroup=i['resourceGroup'],
                   Location=i['location'], UsedBytes=i['usedBytes'], MaxSizeBytes=i['maxSizeBytes'],
                   Status=i['status'], EarliestRestoreDate=i['earliestRestoreDate'],
                   Type=i['type'], Tier=i['tier'], Collation=i['collation'])
        db.session.add(row)
    
    db.session.commit() # commit the changes to the db 
    # dnspod
    login_token = os.getenv('LOGIN_TOKEN')  
    dp_obj = IcicleDnsPod(login_token)
    dns_list = dp_obj.get_dns_list()
    for i in dns_list:
        id = i['id']
        name = i['name']
        created_on = i['created_on']
        updated_on = i['updated_on']
        records = i['records']
        row = DnsPodDomains(DomainId=id, DomainName=name, CreationTime=created_on, UpdateTime=updated_on, Records=records)
        db.session.add(row)

    dns_records = dp_obj.get_record_list()
    for i in dns_records:
        ParentDomain = i['domain']['name']
        for j in i['records']:
            ChildDomain = j['name']
            Value = j['value'].rstrip('.')
            UpdateTime = j['updated_on']
            Type = j['type']
            Enabled = j['enabled']
            row = DnsPodRecords(ChildDomain=ChildDomain, ParentDomain=ParentDomain, Value=Value, 
                                UpdateTime=UpdateTime, Type=Type, Enabled=Enabled)
            db.session.add(row)

    db.session.commit() # commit the changes to the db 
    click.echo("All data has been successfully generated.")
