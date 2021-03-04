from cmp.iciclealiyun import IcicleAliyun, MonthData
from cmp.icicleoracle import IcicleOracle
from cmp.icicleazure import IcicleAzure
from cmp.iciclednspod import IcicleDnsPod
from cmp import celery, db
from cmp.models import *
import os
import datetime
from calendar import monthrange

@celery.task
def get_aliyun_ecs(akid, aksecret, region, AccountName):
    now = datetime.datetime.now().isoformat() # get the current time
    last_m = (datetime.datetime.today() - datetime.timedelta(30)).strftime("%Y-%m") # last month

    #### ECS ####   
    cloud_obj = IcicleAliyun(akid, aksecret, region) # get access to aliyun api
    cloud_servers = cloud_obj.fetch_ecs_info() # fetch ecs data
    cloud_prices = cloud_obj.fetch_price(last_m) # fetch price data of the last month 
    cloud_price_dict = {} # store price data in <instanceid:price> format

    for i in cloud_prices:
        try:
            cloud_price_dict[i['InstanceID']] += i['PretaxAmount']
        except:
            cloud_price_dict[i['InstanceID']] = i['PretaxAmount']
    # obtain value of each column
    for i in cloud_servers:
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
            if InstanceId in cloud_price_dict.keys():
                MonthPrice = str(cloud_price_dict[InstanceId])
        except Exception as e:
            MonthPrice = "Null"
        # instantiate ecs table class
        row = AliyunVm(InstanceId=InstanceId, InstanceName=InstanceName, ZoneId=ZoneId, \
                RegionId=RegionId, AccountName=AccountName, InstanceType=InstanceType, \
                PrivateIp=PrivateIp, PublicIP=PublicIP, Memory=Memory, Cpu=Cpu, \
                OSName=OSName, CreationTime=CreationTime, MonthPrice=MonthPrice)
        db.session.add(row) # add a row to the db session
    db.session.commit() # commit the changes to the db

@celery.task
def get_aliyun_rds(akid, aksecret, region, AccountName):
    now = datetime.datetime.now().isoformat() # get the current time
    last_m = (datetime.datetime.today() - datetime.timedelta(30)).strftime("%Y-%m") # last month
    cloud_obj = IcicleAliyun(akid, aksecret, region) # get access to aliyun api
    cloud_rdses = cloud_obj.fetch_rds_ins_ver()
    cloud_prices = cloud_obj.fetch_price(last_m) # fetch price data of the last month 
    cloud_price_dict = {} # store price data in <instanceid:price> format

    for i in cloud_prices:
        try:
            cloud_price_dict[i['InstanceID']] += i['PretaxAmount']
        except:
            cloud_price_dict[i['InstanceID']] = i['PretaxAmount']

    for i in cloud_rdses:
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
            MonthPrice = str(cloud_price_dict[DBInstanceId])
        except:
            MonthPrice = ""
        try:
            DBInstanceDescription = i['DBInstanceDescription']
        except:
            DBInstanceDescription = DBInstanceId

        row = AliyunRds(DBInstanceId=DBInstanceId, ConnectionString=ConnectionString,\
                        AccountName=AccountName, ZoneId=ZoneId, RegionId=RegionId,\
                        Port=Port, DBInstanceDescription=DBInstanceDescription, DBInstanceClass=DBInstanceClass,\
                        DBInstanceCPU=DBInstanceCPU, DBInstanceMemory=DBInstanceMemory, DBInstanceStorage=DBInstanceStorage,\
                        CreationTime=CreationTime, ExpireTime=ExpireTime, Engine=Engine, SecurityIPList=SecurityIPList,\
                        MonthPrice=MonthPrice)
        db.session.add(row)

    db.session.commit() # commit the changes to the db

@celery.task
def get_aliyun_dnat(akid, aksecret, region):
    cloud_obj = IcicleAliyun(akid, aksecret, region) # get access to aliyun api

    dnat_list = cloud_obj.fetch_dnat_entries()
    # insert into db
    for i in dnat_list:
        ExternalPort = i['ExternalPort']
        ExternalIp = i['ExternalIp']
        InternalPort = i['InternalPort']
        InternalIp = i['InternalIp']
        row = AliyunDnat(ExternalPort=ExternalPort, ExternalIp=ExternalIp, InternalPort=InternalPort, InternalIp=InternalIp)
        db.session.add(row)
    db.session.commit() # commit the changes to the db

@celery.task
def get_aliyun_cdn(akid, aksecret, region):
    cloud_obj = IcicleAliyun(akid, aksecret, region) # get access to aliyun api

    cdn = cloud_obj.fetch_cdn()
    for i in cdn:
        DomainName = i['DomainName']
        Cname = i['Cname']
        CreationTime = i['GmtCreated']
        Coverage = i['Coverage']
        OriginAddress = i['Sources']['Source'][0]['Content']
        row = AliyunCdn(DomainName=DomainName, Cname=Cname, CreationTime=CreationTime,
                    Coverage=Coverage, OriginAddress=OriginAddress)
        db.session.add(row)
    db.session.commit() # commit the changes to the db

@celery.task
def get_aliyun_waf(akid, aksecret, region2, AccountName):
    cloud_obj = IcicleAliyun(akid, aksecret, region2) # get access to aliyun api
    waf = cloud_obj.fetch_waf()
    for i in waf:
        DomainName = i['Domain']
        OriginAddress = ','.join(i['Profile']['Rs'])
        HttpPort = ','.join([str(j) for j in i['Profile']['HttpPort']])
        HttpsPort = ','.join([str(j) for j in i['Profile']['HttpsPort']])
        Cname = i['Profile']['Cname']
        AccountName = AccountName
        row = AliyunWaf(DomainName=DomainName, OriginAddress=OriginAddress, HttpPort=HttpPort,
        HttpsPort=HttpsPort, Cname=Cname, AccountName=AccountName)
        db.session.add(row)
    db.session.commit() # commit the changes to the db

@celery.task
def get_aliyun_ssl(akid, aksecret, region, AccountName):
    cloud_obj = IcicleAliyun(akid, aksecret, region) # get access to aliyun api
    cert= cloud_obj.fetch_cert()['CertificateList']
    for i in cert:
        CertName = i['name']
        CertId = i['id']
        DomainName = i['sans']
        Issuer = i['issuer']
        StartDate = i['startDate']
        EndDate = i['endDate']
        AccountName = AccountName
        row = AliyunSsl(CertName=CertName, CertId=CertId, DomainName=DomainName, Issuer=Issuer,
        StartDate=StartDate, EndDate=EndDate, AccountName=AccountName)
        db.session.add(row)
    db.session.commit() # commit the changes to the db

@celery.task
def get_aliyun_oss(akid, aksecret, region):
    cloud_obj = IcicleAliyun(akid, aksecret, region) # get access to aliyun api
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
    data_this_month = MonthData(akid, aksecret, region, this_start, this_end)
    data_last_month = MonthData(akid, aksecret, region, last_start, last_end)
    #设置变量
    BucketName = data_this_month.get_buc_name_usage()[0]
    VolThisMon = data_this_month.get_buc_name_usage()[1]
    VolLastMon = data_last_month.get_buc_name_usage()[1]
    ReqThisMon = data_this_month.get_req()
    ReqLastMon = data_last_month.get_req()
    RecvThisMon = data_this_month.get_recv()
    RecvLastMon = data_last_month.get_recv()
    SendThisMon = data_this_month.get_send()
    SendLastMon = data_last_month.get_send()
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

@celery.task
def get_oc_vm():
    oc_obj = IcicleOracle()
    oc_vm_list = oc_obj.makeVmList()
    for i in oc_vm_list:
        row = OcVm(Name=i['display_name'], PrivateIp=i['private_ip'], PublicIp=i['public_ip'],
                   Zone=i['availability_domain'], State=i['lifecycle_state'], Shape=i['shape'],
                   NumOfCpu=i['cpus'], CpuDesc=i['processor_description'], Memory=i['memory'],
                   Bandwidth=i['bandwidth'], CreatedOn=i['time_created'])
        db.session.add(row)
    db.session.commit() # commit the changes to the db

@celery.task
def get_az_vm():
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

@celery.task
def get_az_db():
    az_obj = IcicleAzure()
    az_dbs = az_obj.getDbList()
    for i in az_dbs:
        row = AzDb(Name=i['name'], CreationDate=i['creationDate'], ResourceGroup=i['resourceGroup'],
                   Location=i['location'], UsedBytes=i['usedBytes'], MaxSizeBytes=i['maxSizeBytes'],
                   Status=i['status'], EarliestRestoreDate=i['earliestRestoreDate'],
                   Type=i['type'], Tier=i['tier'], Collation=i['collation'])
        db.session.add(row)
    db.session.commit() # commit the changes to the db

@celery.task
def get_dp_domains():
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
    db.session.commit() # commit the changes to the db

@celery.task
def get_dp_records():
    login_token = os.getenv('LOGIN_TOKEN')
    dp_obj = IcicleDnsPod(login_token)
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
