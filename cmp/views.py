from flask import flash, redirect, url_for, render_template
from sqlalchemy.sql import func
from cmp import app, db
from cmp.models import *
from cmp.tasks import *
import os
from dotenv import load_dotenv

@app.route('/recreate_db')
def recreate_db():
    db.drop_all()
    db.create_all()
    flash('数据库初始化完毕!')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aliyun/ecs')
def ecs():
    rows = db.session.query(AliyunVm.InstanceId, AliyunVm.InstanceName,
           AliyunVm.ZoneId, AliyunVm.RegionId, AliyunVm.AccountName,
           AliyunVm.InstanceType, AliyunVm.PrivateIp, AliyunVm.PublicIP,
           AliyunVm.Memory, AliyunVm.Cpu, AliyunVm.OSName, AliyunVm.CreationTime,
           AliyunVm.MonthPrice, 
           func.count(AliyunDnat.id).label('dnat_items')).outerjoin( 
           AliyunDnat, AliyunVm.PrivateIp==AliyunDnat.InternalIp).group_by(AliyunVm.id).all()
    return render_template('aliyun/aliyun_vm.html', rows=rows)

@app.route('/aliyun/rds')
def rds():
    rows = AliyunRds.query.all()
    return render_template('aliyun/aliyun_rds.html', rows=rows)

@app.route('/aliyun/dnat')
def dnat():
    rows = AliyunDnat.query.all()
    return render_template('aliyun/aliyun_dnat.html', rows=rows)

@app.route('/aliyun/dnat_pip/<private_ip>')
def dnat_pip(private_ip):
    rows = AliyunDnat.query.filter(AliyunDnat.InternalIp==private_ip).all()
    return render_template('aliyun/aliyun_dnat.html', rows=rows)

@app.route('/aliyun/dnat_eip/<public_ip>')
def dnat_eip(public_ip):
    rows = AliyunDnat.query.filter(AliyunDnat.ExternalIp==public_ip).all()
    return render_template('aliyun/aliyun_dnat.html', rows=rows)

@app.route('/aliyun/cdn')
def cdn():
    rows = AliyunCdn.query.all()
    return render_template('aliyun/aliyun_cdn.html', rows=rows)

@app.route('/aliyun/cdn_search/<value>')
def cdn_search(value):
    rows = AliyunCdn.query.filter(AliyunCdn.Cname==value).all()
    return render_template('aliyun/aliyun_cdn.html', rows=rows)

@app.route('/aliyun/waf')
def waf():
    rows = AliyunWaf.query.all()
    return render_template('aliyun/aliyun_waf.html', rows=rows)

@app.route('/aliyun/waf_search/<value>')
def waf_search(value):
    rows = AliyunWaf.query.filter(AliyunWaf.Cname==value).all()
    return render_template('aliyun/aliyun_waf.html', rows=rows)

@app.route('/aliyun/ssl')
def ssl():
    rows = AliyunSsl.query.all()
    return render_template('aliyun/aliyun_ssl.html', rows=rows)

@app.route('/aliyun/oss')
def oss():
    rows = AliyunOss.query.all()
    return render_template('aliyun/aliyun_oss.html', rows=rows)

@app.route('/oraclecloud/vm')
def oc_vm():
    rows = OcVm.query.all()
    return render_template('oraclecloud/oc_vm.html', rows=rows)

@app.route('/azure/vm')
def az_vm():
    rows = AzVm.query.all()
    return render_template('azure/az_vm.html', rows=rows)

@app.route('/azure/db')
def az_db():
    rows = AzDb.query.all()
    return render_template('azure/az_db.html', rows=rows)

@app.route('/dnspod/domains')
def dp_domains():
    rows = DnsPodDomains.query.all()
    return render_template('dnspod/dp_domains.html', rows=rows)

@app.route('/dnspod/records')
def dp_records():
    rows = db.session.query(DnsPodRecords.ChildDomain, 
           DnsPodRecords.ParentDomain, DnsPodRecords.Value,
           DnsPodRecords.UpdateTime, DnsPodRecords.Type,
           DnsPodRecords.Enabled, func.count(AliyunDnat.id).label('dnat_items'),
           func.count(AliyunCdn.id).label('cdn_items'),
           func.count(AliyunWaf.id).label('waf_items')).outerjoin(
           AliyunDnat, DnsPodRecords.Value==AliyunDnat.ExternalIp).outerjoin(
           AliyunCdn, DnsPodRecords.Value==AliyunCdn.Cname).outerjoin(
           AliyunWaf, DnsPodRecords.Value==AliyunWaf.Cname).group_by(DnsPodRecords.id).all()
    return render_template('dnspod/dp_records.html', rows=rows)

def get_aliyun_user_lists():
    """
    读取环境变量，返回阿里云账号相关信息。
    """
    load_dotenv(dotenv_path='/cmp/env/.env') # load environment variables
    # aliyun user1 settings
    user1_akid = os.getenv('user1_AccessKeyId')
    user1_aksecret = os.getenv('user1_AccessKeySecret')
    user1_region = os.getenv('user1_RegionId')
    user1_region2 = os.getenv('user1_RegionId2')
    user1_AccountName = os.getenv('user1_AccountName')
    user1_list = [user1_akid, user1_aksecret, user1_region, user1_region2, user1_AccountName]
    # aliyun user2 settings
    user2_akid = os.getenv('user2_AccessKeyId')
    user2_aksecret = os.getenv('user2_AccessKeySecret')
    user2_region = os.getenv('user2_RegionId')
    user2_region2 = os.getenv('user2_RegionId2')
    user2_AccountName = os.getenv('user2_AccountName')
    user2_list = [user2_akid, user2_aksecret, user2_region, user2_region2, user2_AccountName]
    user_lists = [user1_list, user2_list]
    return user_lists

@app.route('/update/aliyun/ecs')
def update_aliyun_ecs():
    """
    更新ecs数据。
    """
    db.session.query(AliyunVm).delete() 
    db.session.commit() # commit the changes to the db
    user_lists = get_aliyun_user_lists()
    for i in user_lists:
        get_aliyun_ecs.delay(i[0], i[1], i[2], i[4]) # i[0]是accesskey,i[1]secret,i[2]region1,i[3]region2,i[4]账号名
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('ecs'))

@app.route('/update/aliyun/rds')
def update_aliyun_rds():
    db.session.query(AliyunRds).delete() 
    db.session.commit() # commit the changes to the db
    user_lists = get_aliyun_user_lists()
    for i in user_lists:
        get_aliyun_rds.delay(i[0], i[1], i[2], i[4])
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('rds'))

@app.route('/update/aliyun/dnat')
def update_aliyun_dnat():
    db.session.query(AliyunDnat).delete() 
    db.session.commit() # commit the changes to the db
    user_lists = get_aliyun_user_lists()
    for i in user_lists:
        get_aliyun_dnat.delay(i[0], i[1], i[2])
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('dnat'))

@app.route('/update/aliyun/cdn')
def update_aliyun_cdn():
    db.session.query(AliyunCdn).delete() 
    db.session.commit() # commit the changes to the db
    user_lists = get_aliyun_user_lists()
    for i in user_lists:
        get_aliyun_cdn.delay(i[0], i[1], i[2])
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('cdn'))

@app.route('/update/aliyun/waf')
def update_aliyun_waf():
    db.session.query(AliyunWaf).delete() 
    db.session.commit() # commit the changes to the db
    user_lists = get_aliyun_user_lists()
    for i in user_lists:
        get_aliyun_waf.delay(i[0], i[1], i[3], i[4])
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('waf'))

@app.route('/update/aliyun/ssl')
def update_aliyun_ssl():
    db.session.query(AliyunSsl).delete() 
    db.session.commit() # commit the changes to the db
    user_lists = get_aliyun_user_lists()
    for i in user_lists:
        get_aliyun_ssl.delay(i[0], i[1], i[3], i[4])
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('ssl'))

@app.route('/update/aliyun/oss')
def update_aliyun_oss():
    db.session.query(AliyunOss).delete() 
    db.session.commit() # commit the changes to the db
    user_lists = get_aliyun_user_lists()
    for i in user_lists:
        get_aliyun_oss.delay(i[0], i[1], i[2])
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('oss'))

@app.route('/update/oc/vm')
def update_oc_vm():
    db.session.query(OcVm).delete() 
    db.session.commit() # commit the changes to the db
    get_oc_vm.delay()
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('oc_vm'))

@app.route('/update/azure/vm')
def update_az_vm():
    db.session.query(AzVm).delete() 
    db.session.commit() # commit the changes to the db
    get_az_vm.delay()
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('az_vm'))

@app.route('/update/azure/db')
def update_az_db():
    db.session.query(AzDb).delete() 
    db.session.commit() # commit the changes to the db
    get_az_db.delay()
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('az_db'))

@app.route('/update/dnspod/domains')
def update_dp_domains():
    db.session.query(DnsPodDomains).delete() 
    db.session.commit() # commit the changes to the db
    get_dp_domains.delay()
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('dp_domains'))

@app.route('/update/dnspod/records')
def update_dp_records():
    db.session.query(DnsPodRecords).delete() 
    db.session.commit() # commit the changes to the db
    get_dp_records.delay()
    flash('数据更新完毕,请刷新页面!')
    return redirect(url_for('dp_records'))
