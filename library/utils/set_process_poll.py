'''
    功能变量读写类
    功能：
        创建公共变量索引:随机生成一个公共变量索引
        修改公共变量:给出一个索引,以及要修改的值
        读取公共变量:给出一个索引,返回公共变量

        creattime:创建时间（datetime)
        completetime:完成时间(datetime)
        username:隶属用户(str)
        complete:本次预约是否完成（bool）
        content:预约日志（list）,文本框显示内容
        statues:预约状态，代表是否预约到座位(bool)
        result:结果,字符串简单表述预约的结果(str),显示在弹窗上面简述
'''

from library.settings import process_poll,process_poll_lock
import random
import datetime


def Creat_Process_Poll_Key(username,Count = 1):
    # TODO:防止恶意创建,建议在每次创建时清除内容,前期不用考虑因为凌晨服务器自动重启
    if Count > 5:
        return None
    unixtime = int(datetime.datetime.now().timestamp() * 1000)
    random_key = ("".join([random.choice("0123456789ABCDEF") for i in range(16)])) + str(unixtime) + username
    
    if random_key in process_poll:
        return Creat_Process_Poll_Key(username,Count + 1)
    else:
        process_poll_lock.acquire()     # 加锁
        process_poll[random_key] = {
                'creattime':datetime.datetime.now(),
                'completetime':None,
                'username':username,
                'complete':None,
                'content':[],
                'statues':None,
                'result':None,
            }
        process_poll_lock.release()     # 释放
        return random_key


def Change_Process_Poll_Value(key,username,complete,content,statues,result):
        process_poll_lock.acquire()     # 加锁


        if complete == True:
            process_poll[key]['completetime'] = datetime.datetime.now(),
            process_poll[key]['complete'] = complete
            process_poll[key]['content'] = content
            process_poll[key]['statues'] = statues
            process_poll[key]['result'] = result
        else:
            process_poll[key]['complete'] = complete
            process_poll[key]['content'] = content
            process_poll[key]['statues'] = statues
            process_poll[key]['result'] = result
        process_poll_lock.release()     # 释放



def Read_Process_Poll_Value(key,get_value = None):
    Get_Value = process_poll.get(key,None)
    if get_value == None:
        return Get_Value
    else:
        return Get_Value.get(get_value,None)


def Check_Process_Poll_Key(key):
    if key in process_poll:
        return True
    else:
        return False

def Clear_Process_Poll():
    process_poll_lock.acquire()     # 加锁
    process_poll.clear()
    process_poll_lock.release()     # 释放

def Read_all():
    return process_poll