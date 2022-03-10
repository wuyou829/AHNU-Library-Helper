'''
    页面视图生成模块
    功能：本模块是对web/views传来的值进行整理,返回一个字典用来传递给页面视图
'''
import datetime
from Core.models import Broadcast
from Web.form import UserForm,UploadFileForm
from utils.tools import uuid_encode

from utils.set_process_poll import Creat_Process_Poll_Key

def login_page_dict(warn_info):
    server_boot = datetime.datetime.strptime('06:00','%H:%M').time()
    server_shutdown = datetime.datetime.strptime('23:00','%H:%M').time()
    now_time = datetime.datetime.now().time()
    if (now_time < server_boot) or (now_time > server_shutdown):
        warn_info.append('图书馆服务器已经关机,新用户将无法登陆')
    userfrom = UserForm()
    content = {
        'Warn_info':"nodisplay",
        'userfrom':userfrom,
        'broadcastcontent':read_broadcast(),
        'warn_info':warn_info,
    }
    return content

def fast_page_dict(fast_record,warn_info,username,Code = None):
    '''
        功能:Fast界面展示数据(主页展示信息)
        参数:
            fast_record: 获取的历史记录queryset
            warn_info: 这是一个列表展示了所有的警告信息，空列表自动不显示警告信息
            username: 如果传递username代表这是模态框展示
        返回:返回一个dict
    '''

    # 生成input标签
    input_lable = Creat_Process_Poll_Key(username)

    fast_history_list = []
    list_count = 0
    for i in fast_record:
        fast_history_list.append({
            "count":list_count,
            "seatname":i.seatname,
            "begintimestr":i.begintimestr,
            "endtimestr":i.endtimestr,
            "pushnum":i.pushnum,
            "is_today":i.is_today,
            "auto_reserve":i.auto_reserve,
            "creat_time":i.createtime.strftime("%m/%d %H:%M")
        })
        list_count +=1

    content = {
                "nav_select":["active","","","",""],
                "history":fast_history_list,
                "warn_info":warn_info,
                "broadcastcontent":read_broadcast(),
                "input_lable":input_lable,
        }
    if Code != None:
        content["show_model"] =  "$('#staticBackdrop').modal('show');"
        content["seat_process"] = "seatprocess();"
        content["username"] = username
        content["creattime"] = datetime.datetime.now().strftime("%H:%M")
        content["input_lable"] = Code


    return content

def clock_page_dict(clock_assignment,wxenable,warn_info):
    '''
        功能:展示定时预约信息
        参数:
            clock_assignment: 获取的定时预约queryset
            wxenable: 该用户是否注册了微信
            warn_info: 这是一个列表展示了所有的警告信息，空列表自动不显示警告信息
        返回:返回一个dict
    '''
    week_day = ["周一","周二","周三","周四","周五","周六","周日"]
    Display_Assignment = []
    for i in range(7):
        Display_Assignment.append({
            "weekday" :week_day[i],
            "start_time":"",
            "end_time":"",
            "seatname":"",
            "have_assignment":False,
            "broadcastcontent":read_broadcast(),
        })
    for i in clock_assignment:
        Display_Assignment[i.Reservation_Day-1]["start_time"] = i.begintimestr
        Display_Assignment[i.Reservation_Day-1]["end_time"] = i.endtimestr
        Display_Assignment[i.Reservation_Day-1]["seatname"] = i.seatname
        Display_Assignment[i.Reservation_Day-1]["have_assignment"] = True

    content = {
        "nav_select":["","active","","",""],
        "assignment_dict":Display_Assignment,
        "warn_info":warn_info,
        "wxenable":wxenable,
    }
    return content

def account_page_dict(user_info,warn_info):
    '''
        功能:展示用户信息
        参数:
            user_info: 获取到的用户信息model类
            warn_info: 这是一个列表展示了所有的警告信息，空列表自动不显示警告信息
        返回:返回一个dict
    '''
    display_username = user_info.username
    display_password = user_info.password
    display_password = display_password[:2] + '******'
    display_WXID =  user_info.wxname
    display_UUID = uuid_encode(user_info.uuid.hex)
    display_UUID = "/bind-" + display_UUID
    if display_WXID is None:
        display_WXID = '暂未绑定'

    content = {
        "nav_select":["","","active","",""],
        "display_username":display_username,
        "display_password":display_password,
        "display_WXID":display_WXID,
        "display_UUID":display_UUID,
        "warn_info":warn_info,
        "broadcastcontent":read_broadcast(),
    }
    return content

def qrcode_page_dict(qrcode_record,have_alert = False,is_warn = False,message = []):
    '''
        功能:二维码扫描界面展示数据
        参数:
            qrcode_record: 二维码历史记录
            have_alert: 是否存在顶栏的警告框
            is_warn: 是否为警告框
            message: 警告框消息
        返回:返回一个dict
    '''
    qrcode_record_list = []
    for i in qrcode_record:
        ischeck = i.ischeck
        isable = i.isable
        if ischeck is False and isable is False:
            note = "图片错误"
        elif ischeck is True and isable is False:
            note = "已经存在"
        else:
            note = "验证成功"
        qrcode_record_list.append({
            "seatname" : i.seatname,
            "isable" : i.isable,
            "note":note,
            "creat_time":i.createtime.strftime("%m/%d %H:%M")

        })
    form = UploadFileForm()
    content = {
        "nav_select":["","","","active"],
        "have_alert":have_alert,
        "is_warn":is_warn,
        "message":message,
        "form": form,
        "qrcode_record":qrcode_record_list,
        "broadcastcontent":read_broadcast(),
    }
    return content
    
def other_page_dict():
    content = {
        "nav_select":["","","",""],
        "broadcastcontent":read_broadcast(),
    }
    return content

def read_broadcast():
        # 读取广播数据库
    Get_broadcast = Broadcast.objects.filter().order_by("-GetMessageTime")
    if( len(Get_broadcast) < 1 ):
        broadcastcontent = ""
    else:
        broadcastcontent = Get_broadcast[0].content
    return broadcastcontent
