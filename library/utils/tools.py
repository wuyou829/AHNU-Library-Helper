
import datetime
from Core.models import User

def system_message_slove(get_dict):
    '''
    系统消息处理
        当好友被删除时
        {
            'event': 'EventFriendMsg',
            'robot_wxid': 'wxid_*****x22',
            'robot_name': '',
            'type': 10000,
            'from_wxid': '',
            'from_name': '',
            'final_from_wxid': 'wxid_*********22',
            'final_from_name': 'S****w',
            'to_wxid': 'wxid_*****22',
            'msg': 'S****w开启了朋友验证，你还不是他（她）朋友。请先发送朋友验证请求，对方验证通过后，才能聊天。<ahref="weixin://findfriend/verifycontact">发送朋友验证</a>'
        }
        当添加好友时
        {
            'event': 'EventFriendMsg',
            'robot_wxid': 'wxid**********9x22',
            'robot_name': '',
            'type': 10000,
            'from_wxid': '',
            'from_name': '',
            'final_from_wxid': 'wx******22',
            'final_from_name': 'S*****w',
            'to_wxid': 'w****2',
            'msg': '以上是打招呼的内容'
        }

    '''
    if "请先发送朋友验证请求" in get_dict['msg']:
        # 被删除好友
        Get_User = User.objects.filter(wxid = get_dict['final_from_wxid'])
        for item in Get_User:
            item.wxid = None
            item.wxname  = None
            item.wxidenable = False
            item.save()

def weekstr_to_num(Str):
    SN = {
        "周一":1,
        "周二":2,
        "周三":3,
        "周四":4,
        "周五":5,
        "周六":6,
        "周日":7,
    }
    return SN.get(Str,None)


def weekstr_to_num_sub_one(Str):
    SN = {
        "周一":7,
        "周二":1,
        "周三":2,
        "周四":3,
        "周五":4,
        "周六":5,
        "周日":6,
    }
    return SN.get(Str,None)

def uuid_encode(uuid):
    # uuid加密,很简单的加密方式,在UUID前面加上时间缀来判定时间是否超时
    # 举例：208a2cd0-8365-11ec-b14e-8112767ea2bc，8-4-4-4-12
    time_correct = hex(int(datetime.datetime.now().timestamp ()))[2:]
    return time_correct + "_" + uuid


def UUID_decode(code):
    # uuid解密
    time_now = int(datetime.datetime.now().timestamp ())
    try:
        time_check = int("0x" + code.split("_")[0],16)
        uuid = code.split("_")[1]
        if time_now - time_check >= 600:
            result = {
                "status" : False,
                "uuid":"",
                "message":"代码超时",
            }
        else:
            result = {
            "status" : True,
            "uuid":uuid,
            "message":"",
        }
        
    except:
        result = {
            "status" : False,
            "uuid":"",
            "message":"代码格式错误",
        }
    finally:
        return result
        