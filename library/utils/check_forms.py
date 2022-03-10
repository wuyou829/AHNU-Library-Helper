'''表单检验工具

本模块作用是对输入的表单内容进行检测
检测内容：
    check_push_num : 检测推进数量是否合法
    check_seat_name : 检测座位名称是否合法
    check_reserve_time : 检测申请预约时间段是否合法

'''

import datetime
from .user_setting import user_setting 
from . import seat_dict

def check_push_num(pushnum):
    '''
        功能: 检验推进座位个数是否正确
        参数: 
            pushnum: 代表推进数目的类型

        返回:
            一个字典,字典内容描述描述了这个推进座位的合法性
            result_dict = {
                "status":False,             描述这次数值检验的结果True为正确,False为错误
                "push_num":0,               描述推进数目,只有检验正确才有值
                "message":"推进数字不合法"   描述检验错误的原因,只有检验错误才有值
            }
    '''
    try:
        num = int(pushnum)
        if num < 1 or num > user_setting["max_push"]:
            result_dict = {
                "status":False,
                "push_num":0,
                "message":"推进数字不合法"
            }
        else:
            result_dict = {
                "status":True,
                "push_num":num,
                "message":""
            }
    except:
        result_dict = {
            "status":False,
            "push_num":0,
            "message":"数据异常"
        }
    finally:
        return result_dict


def check_seat_name(seat_name):
    '''
        功能: 检验座位的合法性
        参数: 座位名
        返回: 一个字典类型
            result_dict = {
                "status":True,              描述本次检验的结果,False为异常,True为正常
                "sno":321   ,               座位编号-仅转换结果正确有效
                "sname":"nsk***",           座位名 - 仅转换结果正确有效
                "message":""                异常信息-仅转换结果错误有效
            }
    '''
    get_sno = seat_dict.name_to_num.get(seat_name,None)
    if get_sno is None:
        result_dict = {
            "status":False,
            "sno":-1,
            "sname":"",
            "message":"没有查询到您输入的座位"
        }
    else:
        result_dict = {
            "status":True,
            "sno":get_sno,
            "sname":seat_name,
            "message":""
        }
    return result_dict


def check_reserve_time(begintime,endtime,is_today):
    '''
        功能: 检验时间的合法性
        备注:
            开始时间早于结束时间
            开始时间晚于8:00
            结束时间早于22:00
            时间间隔大于1小时
            今天预约时,起始时间应晚于当前时间10分钟
        参数:
            begintime (str)
            endtime (str)
            is_today (bool)
        返回: 一个字典类型
            result = {
                "status" : True,                预约结果反馈-False为异常,True为正常
                "begintime_str" : "08:00",      格式化后的开始时间,仅status为True时有值
                "endtime_str" : "22:00",        格式化后的结束时间,仅status为True时有值
                "message" : ""                  错误信息,仅status为False时有值    
            } 
    '''
    result = {
        "status" : False,
        "begintime_str" : "",
        "endtime_str" : "",
        "message" : ""
    }
    try:
        start = datetime.datetime.strptime(begintime, "%H:%M")
        start_add_an_hour = start + datetime.timedelta(hours=1)
        start_sub_ten_minutes = start - datetime.timedelta(minutes=10)
        end = datetime.datetime.strptime(endtime, "%H:%M")

        start_limit = datetime.datetime.strptime("08:00", "%H:%M")
        end_limit = datetime.datetime.strptime("22:05", "%H:%M")

        if start >= end:
            # 开始时间晚于结束
            raise Exception("开始时间应该早于结束时间")

        if start_add_an_hour >= end:
            # 时间间隔小于1小时
            raise Exception("时间间隔不足1小时")

        if (start < start_limit) or (end < start_limit):
            # 开始时间不符合条件
            raise Exception("请求应该晚于8:00")

        if (start > end_limit) or (end > end_limit):
            # 结束时间不符合条件
            raise Exception("请求时间应该早于22:00")
        if is_today:
            # 如果为今天，那么应该晚于当前时间
            if start_sub_ten_minutes.time() < datetime.datetime.now().time():
                raise Exception("今日预约-时间应该晚于当前时间10分")
        
        result["status"] = True
        result["begintime_str"] = start.strftime("%H:%M")
        result["endtime_str"] = end.strftime("%H:%M")
        result["message"] = ""
    except ValueError:
        result["status"] = False
        result["begintime_str"] = ""
        result["endtime_str"] = ""
        result["message"] = "数据异常,请刷新界面"
    except Exception as er:
        result["status"] = False
        result["message"] = str(er)
    finally:
        return result