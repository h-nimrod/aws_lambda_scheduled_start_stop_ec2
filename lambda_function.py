# coding: utf-8


################################################################################
# 自動起動
#   対象のEC2のタグに Scheduled-Start を作成し、起動したい時刻(24時間表記 0-23)を記載する
#
# 自動停止
#   対象のEC2タグに Scheduled-Stop を作成し、起動したい時刻(24時間表記 0-23)を記載する
################################################################################

import sys
import boto3
import collections
import time
from pytz import timezone
import datetime
import japanese_holiday
from botocore.client import ClientError
import MyJST

ec2 = boto3.client('ec2')
#ec2 = boto3.client('ec2', region_name='ap-northeast-1')
jst = MyJST.MyJST()

def lambda_handler(event, context):
    get_jst_now(True)
    manipulate_instances()

def manipulate_instances():
    #instances = get_instances(['Name'])
    instances = get_instances()
    
    cnt = 0
    for instance in instances:
        ret = manipulate_instance(instance)
        if ret != None :
            cnt += 1

    return cnt

def manipulate_instance(instance):
    """
    @param instance 
    @param boot True: boot/start, False: shutdown/stop
    @return None: done nothing, True: instance started, False instance stopped
    """

    status = get_status(instance)
    name = get_instance_name(instance)
    #print "status: " + name + " -> " + status
    if status == 'terminated':
        return None

    #
    # holiday stop condition
    #
    stop_holiday = is_match_trigger_stop_holiday(instance)
    if stop_holiday == True :
        stop_ec2(instance)
        return False
        
    #
    # daily condition
    #
    boot = is_match_trigger_hour(instance)
    if boot == None:
        return None
    elif boot : 
        # 起動
        start_ec2(instance)
        return True
    else :
        # 停止
        stop_ec2(instance)
        return False

    return None
                

def is_match_trigger_hour(instance):
    """
    定時実行判定
    @retune None: N/A, True: should boot/start, False: should shutdown/stop
            もし 開始と停止が同じ時刻ならば開始を優先
    """

    boot_hour = get_boot_hour(instance)
    shutdown_hour = get_shutdown_hour(instance)

    if boot_hour == None and shutdown_hour == None:
        return None
    if boot_hour != None and boot_hour == shutdown_hour:
        print "[warning] 開始と停止に同じ時刻が設定されています"

    hour_now = get_hour_now()

    if boot_hour == hour_now:
        return True
    elif shutdown_hour == hour_now:
        return False

    return None


def is_match_trigger_stop_holiday(instance):
    """
    休日のみ停止判定

    @return  None: shuld do nothing, True: should shutdown/stop
    """

    if is_weekday():
        return None

    shutdown_hour = get_shutdown_holiday(instance)

    if shutdown_hour == None :
        return None

    if shutdown_hour == True:
        return True

    if shutdown_hour == get_hour_now():
        return True
    
    return None
    


def get_tags(instance):
    if 'Tags' not in instance:
        return {}

    tags = { t['Key']: t['Value'] for t in instance['Tags'] }
    return tags


def get_instance_name(instance):
    tags = get_tags(instance)

    name = tags['Name'] if "Name" in tags else "(unknown)"
    return name + ":" + get_instance_id(instance)


def get_instance_id(instance):
    return instance['InstanceId']


def get_status(instance):
    return instance['State']['Name']


def is_boot(instance):
    tags = get_tags(instance)

    tag = "Scheduled-Start"
    if tag in tags:
        return True
    
    return False


def get_boot_hour(instance):
    tags = get_tags(instance)

    tag = "Scheduled-Start"
    if tag in tags:
        h_str = tags[tag]
        if h_str.isdigit():
            return int(h_str) % 24
        else :
            print "hour format must be in 0-23, invalid format:" + h_str

    return None


def is_shutdown(instance):
    tags = get_tags(instance)

    tag = "Scheduled-Stop"
    if tag in tags:
        return True

    tag = "Scheduled-Stop-Holiday"
    if tag in tags:
        return True

    return False


def get_shutdown_hour(instance):
    tags = get_tags(instance)

    tag = "Scheduled-Stop"
    if tag in tags:
        h_str = tags[tag]
        if h_str.isdigit():
            return int(h_str) % 24
        else :
            print "hour format must be in 0-23, invalid format:" + h_str
    return None


def get_shutdown_holiday(instance):
    """
    休日のみ停止判定
    
    @return True: 常に停止, int: 停止時刻(hour)
    """
    tags = get_tags(instance)

    tag = "Scheduled-Stop-Holiday"
    if tag in tags:
        h_str = tags[tag]
        if h_str.isdigit():
            return int(h_str) % 24
        else :
            return True
    return None


def get_jst_now(force=False):
    return jst.get_jst_now(force)


def get_hour_now():
    return get_jst_now().hour


# 平日判定
def is_weekday():
    return jst.is_weekday()


# 祝日判定 (not 土日)
def is_holiday():
    return jst.is_holiday()
    
def get_instances(tag_names=None):
    Filters = None
    if tag_names != None:
        Filters=[
            {
                'Name': 'tag-key',
                'Values': tag_names
            }
        ]

    if Filters != None:
        reservations = ec2.describe_instances(Filters)['Reservations']
    else:
        reservations = ec2.describe_instances()['Reservations']

    return sum([
        [i for i in r['Instances']]
        for r in reservations
    ], [])

def get_instances_old(tag_names):
    reservations = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag-key',
                'Values': tag_names
            }
        ]
    )['Reservations']

    return sum([
        [i for i in r['Instances']]
        for r in reservations
    ], [])



def start_ec2(instance):
    status = get_status(instance)
    if status == "running" or status == "terminated" :
        print "not start your instance: " + get_instance_name(instance) + ", status=" + status
        return None

    if sys.flags.debug:
        ret = True
    else:
        res = boto3.resource('ec2')
        target = res.Instance(get_instance_id(instance))
        if status == "stopping":
            print "your instance " + get_instance_name(instance) + " has not been stopped yet, try to wait til stop"
            target.wait_until_stopped()
    
        ret = target.start()
        print ret
    print 'started your instance: ' + get_instance_name(instance)
    return ret


def stop_ec2(instance):
    status = get_status(instance)
    if status != "running" :
        print "not stop your instance: " + get_instance_name(instance) + ", status=" + status
        return None
    
    if sys.flags.debug:
        ret = True
    else:
        res = boto3.resource('ec2')
        target = res.Instance(get_instance_id(instance))
        ret = target.stop()
        print ret
    print 'stopped your instance: ' + get_instance_name(instance)
    return ret

