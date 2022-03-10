from django.http import HttpResponse
from utils.record_wxmessage import message_recording
from utils.tools import system_message_slove
from utils.tools import UUID_decode
from utils.wx_communication import send_message
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .models import Broadcast
from utils.user_setting import user_setting
from Core.models import Signin_Assignment,Assignment

@csrf_exempt                                                    # 跨站请求——微信允许消息接口接入
def StringAnalyse(request):
    '''
        调用：可爱猫接收到消息之后调用
        功能：提取接收的消息，传入指定函数去处理
        主函数中重要的变量：
            Message_Info : 保存当前处理消息的robotwxid,wxid,wxname,message-使用字典引用
    '''
    body_dict = eval(request.body.decode('utf-8'))                      # 解析数据成字典类型
    if (body_dict["type"] !=1) and (body_dict["type"] !=10000):          # 只接收文字信息,1为普通消息10000为系统消息
        return HttpResponse()
    if body_dict["event"] not in 'EventFriendMsg':                      # 只接收好友消息
        return HttpResponse()
    if body_dict["type"] == 10000:                                       # 系统消息处理
        system_message_slove(body_dict)

    Message_Info = message_recording(body_dict)                         # 数据库接收到的信息
    if '/bind-' in Message_Info['message']:
        # 绑定用户信息
        Bind(Message_Info)
    

    elif ('【广播】' in Message_Info['message']) and (Message_Info['wxid'] == user_setting['admin_wxid']):
        # 广播信息
        Sendbroadcast(Message_Info)

    elif ('【清除广播】' in Message_Info['message']) and (Message_Info['wxid'] == user_setting['admin_wxid']):
        # 清除广播信息
        clear_broadcast(Message_Info)


    elif '网站' in Message_Info['message']:
        user_function(Message_Info)


    return HttpResponse()



def Bind(Message_Info):
    '''
        用户信息与图书馆用户绑定
        信息格式:/bind-fc65aff5-7a89-11ec-83d7-c12cc1e1a505
    '''
    _ = Message_Info['message'].replace('/bind-','')
    uuid_check = UUID_decode(_)
    if uuid_check.get("status",False) == False:
        Message = '绑定失败,原因:绑定代码格式错误。'
        send_message(Message_Info['wxid'],Message)
        return HttpResponse()
        
    Get_UUID = uuid_check.get("uuid","none")
    Get_User = User.objects.filter(uuid = Get_UUID)     # 获取属于该UUID的用户

    Get_UUID_User = User.objects.filter(wxid = Message_Info['wxid'])    # 获取绑定微信号的用户
    change = False
    for item in Get_UUID_User:
        # 修改User库
        item.wxid = None
        item.wxname = None
        item.wxidenable = False
        item.save()
        
        # 删除Assignment的所有定时信息
        Assignment.objects.filter(User = item).delete()
        Signin_Assignment.objects.filter(User = item).delete()

        # 删除
        change  = True
        

    if len(Get_User) == 1:
        Get_User = Get_User[0]
        Get_User.wxid = Message_Info['wxid']
        Get_User.wxname = Message_Info['wxname']
        Get_User.wxidenable = True
        Get_User.save()
        if change:
            Message = '绑定状态已经修改,原用户的定时计划已被删除。\n新用户:{0}\n注意:在您使用本工具期间请不要删除好友,我们需要在每次定时预约时提醒您,以免您因忘记本系统的存在而导致图书馆座位多次违约。'.format(Get_User.username)
        else:
            Message = '绑定成功\n用户:{0}\n您可以正常使用本系统了\n注意:在您使用本工具期间请不要删除好友,我们需要在每次定时预约时提醒您,以免您因忘记本系统的存在而导致图书馆座位多次违约。'.format(Get_User.username)
    
    else:
        # 未知错误
        Message = '绑定失败,原因:代码错误'

    send_message(Message_Info['wxid'],Message)
    return HttpResponse()

def Sendbroadcast(Message_Info):
    '''
        用于管理员广播,管理员账号设置位于utils.Usersetting.py
    '''
    content = Message_Info['message'].replace('【广播】','')
    Creat_broadcast = Broadcast(content = content)
    Creat_broadcast.save()
    send_message(Message_Info['wxid'],"广播放置完成")

def clear_broadcast(Message_Info):
    '''
        用于管理员清除广播信息,清除所有的广播信息
    '''
    get_all_broadcast = Broadcast.objects.all()
    get_all_broadcast.delete()
    send_message(Message_Info['wxid'],"广播已经完全清除")

def user_function(Message_Info):
    send_message(Message_Info['wxid'],"http://mars408.fun")