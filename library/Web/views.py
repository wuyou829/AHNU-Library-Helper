from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader, RequestContext

from utils.crawler import Account_Valid
from utils.crawler import QRCode_Check
from Core.models import User
from Core.models import Fastrecord
from Core.models import Assignment
from Core.models import QRCode
from utils.check_forms import check_push_num
from utils.check_forms import check_reserve_time
from utils.check_forms import check_seat_name


from utils.history_record import fast_page_dict
from utils.history_record import clock_page_dict
from utils.history_record import account_page_dict
from utils.history_record import other_page_dict
from utils.history_record import qrcode_page_dict
from utils.history_record import login_page_dict


from utils.tools import weekstr_to_num,weekstr_to_num_sub_one

from utils.scan_qrcode import scan_qrcode
import datetime
import json
import uuid
from library import settings
from utils.fast_threadpool import Upload_Assignment,Check_futhre

from utils.set_process_poll import Creat_Process_Poll_Key,Check_Process_Poll_Key,Read_Process_Poll_Value


from Web.form import UploadFileForm





# 登录
def User_Login(request):
    '''
        功能：登录操作
    '''
    # 获取session
    Login_Username = request.session.get('username', None)

    if Login_Username !=None:
        # 已经登录，跳转到首页
        return HttpResponseRedirect('fast/')
    
    # 没有登录
    if request.method == "POST":
        # 表单数据合法
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        if (username is None) or (password is None):
            content = login_page_dict(['表单不合法'])
            template_view = 'Login/Login.html'
            return render(request, template_view, content)
        try:
            login_check = Account_Valid(username,password)
        except:
            # 服务器没开机或者爬虫失效
            content = login_page_dict(['图书馆服务器无法访问'])
            template_view = 'Login/Login.html'
            return render(request, template_view, content)

        if login_check:
            # 密码验证成功
            # 更新数据库
            Get_User = User.objects.filter(username = username)
            if len(Get_User) == 0:
                # 没有则创建
                Create = User(username = username,password = password)
                Create.save()
            else:
                # 有则修改
                Get_User[0].password = password
                Get_User[0].accountenable = True
                Get_User[0].save()
            Get_User = User.objects.filter(username = username)
            # username保存扫session
            request.session['username'] = username
            # 跳转首页
            return HttpResponseRedirect('/')

        else:
            # 密码验证失败
            content = login_page_dict(['登录失败'])
            template_view = 'Login/Login.html'
            return render(request, template_view, content) 


    # 加载界面（正常加载）
    content = login_page_dict([])
    template_view = 'Login/Login.html'
    return render(request, template_view, content)


# 快速预约
def Fast(request):
    username = request.session.get('username', None)
    # 检验session
    if username is None:
        return HttpResponseRedirect('/')

    # 获取历史数据
    Get_Festrecord = Fastrecord.objects.filter(User = username).order_by('-createtime')[:10]

    # 获取用户信息,这里没有把user保存到session是避免了多端登录时的数据不同步
    Get_User = User.objects.filter(username = username)
    if len(Get_User) != 1:
        # 假如A设备正在登录,B设备删除用户就会出现这种情况
        if 'username' in request.session:
            del request.session['username']
        return HttpResponseRedirect('/')

    # 获取用户信息
    Get_User = Get_User[0]
    
    # 其他异常检测
    display_str = []
    if Get_User.accountenable == False:
        # 用户不可用
        display_str.append("图书馆用户不可用,预约功能将会不成功,请尝试重新登录以重新验证账号密码(前往“用户”，注销本次登录)")

    if Get_User.wxidenable == False:
        # 微信没有绑定
        display_str.append("为了您可以使用完整的功能请前往“用户”绑定微信号,如果您第一次使用本系统,建议您先查阅使用指南（见页脚）")

    # 如果是表单请求
    if request.method == "POST":
        # 获取表单字段
        begintime = request.POST.get('begintime',None)      # str
        endtime = request.POST.get('endtime',None)          # str
        seatname = request.POST.get('seatname',None)        # str
        pushnum = request.POST.get('pushnum',None)          # str
        is_today = request.POST.get('is_today',None)        # str
        is_auto = request.POST.get('is_auto',False)         # str
        process_poll_key = request.POST.get('process_poll_key',None)       # str

        # 检验表单空值
        if (None in [begintime,endtime,seatname,pushnum,is_today,is_auto,process_poll_key]):
            display_str.append("表单异常,请刷新")

            content = fast_page_dict(Get_Festrecord,display_str,username)
            return render(request, 'pages/Fast.html', content)
            
        # 表单正常
        else:
            # 数据转化
            try:
                if is_today == "False":
                    is_today = False
                elif is_today == "True":
                    is_today = True
                else:
                    raise Exception("")

                if is_auto == "True":
                    is_auto = True
                else:
                    is_auto = False
            except:
                display_str.append("表单异常,请刷新")

                content = fast_page_dict(Get_Festrecord,display_str,username)
                return render(request, 'pages/Fast.html', content)
            Time_Check_Result = check_reserve_time(begintime,endtime,is_today)  # 检验时间合法性
            Seatname_Check_Result = check_seat_name(seatname)                   # 检验座位合法性
            Pushnum_Check_Result = check_push_num(pushnum)                      # 检查推进座位数合法性
            # 下面检验数据
            if Time_Check_Result.get("status",False) == False:
                # 时间不合法
                display_str.append("时间不合法:"+Time_Check_Result["message"])
                content = fast_page_dict(Get_Festrecord,display_str,username)
                return render(request, 'pages/Fast.html', content)

            elif Seatname_Check_Result.get("status",False) == False:
                # 座位不合法
                display_str.append("座位不合法:"+Seatname_Check_Result["message"])
                content = fast_page_dict(Get_Festrecord,display_str,username)
                return render(request, 'pages/Fast.html', content)

            elif Pushnum_Check_Result.get("status",False) == False:
                # 推进数不合法
                display_str.append("推进数目不合法")
                content = fast_page_dict(Get_Festrecord,display_str,username)
                return render(request, 'pages/Fast.html', content)

            elif Check_Process_Poll_Key(process_poll_key) == False:
                # input_lable不合法
                display_str.append("值异常，请刷新")
                content = fast_page_dict(Get_Festrecord,display_str,username)
                return render(request, 'pages/Fast.html', content)

            else:
                # 数据检验正常
                reserve_info = {
                    "username":username,
                    "password":Get_User.password,
                    "wxid":Get_User.wxid,
                    "seatname":Seatname_Check_Result['sname'],
                    "seatid":Seatname_Check_Result['sno'],
                    "start_time":Time_Check_Result['begintime_str'],
                    "end_time":Time_Check_Result['endtime_str'],
                    "is_today":is_today,
                    "is_auto":is_auto,
                    "push_num":Pushnum_Check_Result['push_num'],
                    "process_poll_key":process_poll_key,
                }
                try:
                    if Check_futhre(username) is True:
                        display_str.append("重复提交任务,您的任务正在进行,请等待微信反馈结果或者一段时间后自行进入官网查询结果。（如果一直出现本消息,请联系开发任务或者删除账号重新尝试。）")
                        content = fast_page_dict(Get_Festrecord,display_str,username)
                        return render(request, 'pages/Fast.html', content)
                    else:  
                        Upload_Assignment(username,reserve_info)

                        # 将本次计入数据库
                        Creat_Fast_record = Fastrecord(
                            User = Get_User,
                            seatname = Seatname_Check_Result["sname"],
                            sid = Seatname_Check_Result["sno"],
                            begintimestr = Time_Check_Result["begintime_str"],
                            endtimestr = Time_Check_Result["endtime_str"],
                            pushnum = Pushnum_Check_Result["push_num"],
                            is_today = is_today,
                            auto_reserve = is_auto
                        )
                        Creat_Fast_record.save()

                        # 显示结果框
                        content = fast_page_dict(Get_Festrecord,display_str,username,process_poll_key)
                        return render(request, 'pages/Fast.html', content)
                except:
                
                    display_str.append("任务创建失败。")
                    content = fast_page_dict(Get_Festrecord,display_str,username)
                    return render(request, 'pages/Fast.html', content)

    # 其他请求
    

    content = fast_page_dict(Get_Festrecord,display_str,username)
    return render(request, 'pages/Fast.html', content)



# 定时预约
def Clock(request):
    # 检验session
    username = request.session.get('username', None)
    if username is None:
        return HttpResponseRedirect('/')

    # 获取用户详情
    Get_User = User.objects.filter(username = username)
    if len(Get_User) != 1:
        if 'username' in request.session:
            del request.session['username']
        return HttpResponseRedirect('/')

    Get_User = Get_User[0]
    # 获取用户任务
    Get_Assignment = Assignment.objects.filter(User = username)



    # 其他异常检测
    display_str = []
    if Get_User.accountenable == False:
        # 用户不可用
        display_str.append("图书馆用户不可用,请尝试重新登录")

    if Get_User.wxidenable == False:
        # 微信没有绑定
        display_str.append("为了您可以使用完整的功能请前往“用户”绑定微信号")

    # 如果是表单请求
    if request.method == "POST":
        # 获取表单字段
        begintime = request.POST.get('begintime',None)
        endtime = request.POST.get('endtime',None)
        seatname = request.POST.get('seatname',None)
        weeknum = request.POST.get('title_week',None)
        # 检验表单空值
        if (None in [begintime,endtime,seatname]):
            display_str.append("表单异常,请刷新")
            content = clock_page_dict(Get_Assignment,Get_User.wxidenable,display_str)
            return render(request, 'pages/Clock.html', content)

        # 表单正常
        else:
            Time_Check_Result = check_reserve_time(begintime,endtime,False)        # 检验时间合法性
            Seatname_Check_Result = check_seat_name(seatname)                   # 检验座位合法性
            # 下面检验数据
            if Time_Check_Result["status"] == False:
                # 时间不合法
                display_str.append("时间不合法:"+Time_Check_Result["message"])
                content = clock_page_dict(Get_Assignment,Get_User.wxidenable,display_str)
                return render(request, 'pages/Clock.html', content)

            elif Seatname_Check_Result["status"] == False:
                # 座位不合法
                display_str.append("座位不合法:"+Seatname_Check_Result["message"])
                content = clock_page_dict(Get_Assignment,Get_User.wxidenable,display_str)
                return render(request, 'pages/Clock.html', content)

            else:
                # 检验内部用户是否也有一样的任务
                get_assignment = Assignment.objects.filter(seatname = Seatname_Check_Result["sname"],Reservation_Day = weekstr_to_num(weeknum),)
                if len(get_assignment) != 0:
                    display_str.append("已经有用户在本座位使用“按周预约”,请换一个座位重新尝试")
                    content = clock_page_dict(Get_Assignment,Get_User.wxidenable,display_str)
                    return render(request, 'pages/Clock.html', content)
                
                # 数据检验正常
                Assignment.objects.filter(User = Get_User,Reservation_Day = weekstr_to_num(weeknum)).delete()
                # 将本次计入数据库
                Creat_Assignment = Assignment(
                    User = Get_User,
                    seatname = Seatname_Check_Result["sname"],
                    sid = Seatname_Check_Result["sno"],
                    Reservation_Day = weekstr_to_num(weeknum),
                    Run_Day = weekstr_to_num_sub_one(weeknum),
                    begintimestr = Time_Check_Result["begintime_str"],
                    endtimestr = Time_Check_Result["endtime_str"]
                )
                Creat_Assignment.save()

                # 显示结果框
                content = clock_page_dict(Get_Assignment,Get_User.wxidenable,display_str)
                return render(request, 'pages/Clock.html', content)
    # 其他请求
    content = clock_page_dict(Get_Assignment,Get_User.wxidenable,display_str)
    return render(request, 'pages/Clock.html', content)

# 用户
def Account(request):
    username = request.session.get('username', None)
    if username is None:
        return HttpResponseRedirect('/')
    
    Get_User = User.objects.filter(username = username)
    if len(Get_User) != 1:
        if 'username' in request.session:
            del request.session['username']
        return HttpResponseRedirect('/')
    Get_User = Get_User[0]


    display_str = []
    if Get_User.accountenable == False:
        # 用户不可用
        display_str.append("图书馆用户不可用,请在本界面注销账号并重新登录")

    if Get_User.wxidenable == False:
        # 微信没有绑定
        display_str.append("为了您可以使用完整的功能,请在本界面绑定微信号")


    content = account_page_dict(Get_User,display_str)
    template_view = 'pages/Account.html'
    return render(request, template_view, content)

# 二维码登记
def QRCode_reserve(request):
    username = request.session.get('username', None)

    if username is None:
        return HttpResponseRedirect('/')

    Get_User = User.objects.filter(username = username)
    if len(Get_User) != 1:
        if 'username' in request.session:
            del request.session['username']
        return HttpResponseRedirect('/')
    Get_User = Get_User[0]

    # 获取登记记录
    Get_QRCode = QRCode.objects.filter(ischeck = True,isable = True).order_by('-createtime')[:20]


    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # 获取到了文件request.FILES['file']
            codeimg = request.FILES.get('file',None)
            if codeimg is None:
                # 表单错误
                content = qrcode_page_dict(Get_QRCode,True,True,'表单错误,请刷新')
                return render(request, 'pages/QRCode.html', content)

            tail = codeimg.name.split(".")[-1]
            codeimg.name = username +  "-" + uuid.uuid1().hex +  "-" + datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H-%M-%S") + "." + tail
            if ('png' not in tail) and ('jpeg' not in tail) and ('jpg' not in tail):
                content = qrcode_page_dict(Get_QRCode,True,True,'文件格式有误')
                return render(request, 'pages/QRCode.html', content)
            if codeimg.size > 10240000:
                # 文件太大不处理
                content = qrcode_page_dict(Get_QRCode,True,True,'文件太大( 最大10MB ),请压缩后上传')
                return render(request, 'pages/QRCode.html', content)
            else:
                # 这次模型保存用于保存图片
                creat_QR = QRCode(
                    seatname = '/',
                    sid = -1,
                    ischeck = False,
                    isable = False,
                    uploaduser = Get_User,
                    img = codeimg
                )
                creat_QR.save()

                # 检查
                qrcode_result = scan_qrcode(creat_QR.img.path)
                if qrcode_result.get('status',False) is True:
                    Creat = QRCode_Check(creat_QR,qrcode_result['url'])
                    result = Creat.Run()
                    content = qrcode_page_dict(Get_QRCode,True,False,result)
                    return render(request, 'pages/QRCode.html', content)
                else:
                    creat_QR.delete()
                    content = qrcode_page_dict(Get_QRCode,True,True,qrcode_result.get("message","二维码无效"))
                    return render(request, 'pages/QRCode.html', content)
                
    content = qrcode_page_dict(Get_QRCode)
    return render(request, 'pages/QRCode.html', content)


# 关于
def About(request):
    content = other_page_dict()
    template_view = 'pages/About.html'
    return render(request, template_view, content)

# 联系我
def Contact(request):
    content = other_page_dict()
    template_view = 'pages/Contact.html'
    return render(request, template_view, content)

# 声明
def Declaration(request):
    content = other_page_dict()
    template_view = 'pages/Declaration.html'
    return render(request, template_view, content)


# 使用帮助
def Help(request):
    content = other_page_dict()
    template_view = 'pages/Help.html'
    return render(request, template_view, content)




# 登出操作
def Logout(request):
    # 删除 session
    del request.session['username']
    return HttpResponseRedirect('/')



# 获取座位是否支持自动签到
def Search_SeatAuto(request):
    if request.method == "GET":
        seatname = request.GET.get("seatname",None)
        if seatname is None:
            resp = {'statue': -2, 'detail': 'Parameter Error'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        Get_SeatCode = QRCode.objects.filter(seatname = seatname)
        resp = {'statue': 1, 'detail': 'success' , 'able':False}

        for i in Get_SeatCode:
            if i.isable is True:
                resp['able'] = True
                break
        return HttpResponse(json.dumps(resp), content_type="application/json") 

    else:
        resp = {'statue': -1, 'detail': 'Illegal Request'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

# 获取某用户快速预约的进度
def Get_Process(request):
    '''
        详情:
            1. 在Django中存在一个任务进度池,预约程序rw使用,进度程序r使用(不用设锁)
            2. 前端ajax，使用username请求进度
            3. 任务进度池定义在Setting中，settings.process_poll,内容是list类型,表示每一次进度的字符串的集合

        检验算法：
            1. 在Fast点击时添加这个字典键
            2. 在预约过程不断更新字典内容,代表该用户的进度。
            3. 用于点击后Ajax每隔1.0s请求一次进度,不能堆积,需要上一次请求完成后才能继续请求
            4. 预约完成后返回指定值，ajax不再发送,ajax三次获取不到值就不再发送,告知等待微信通知
            5. 每天03:00清除前一天的用户字典      
        settings.process_poll：
            1. 字典 使用username索引
            2. value如下，value为字典
                {
                    'complete' : 完成情况 { True | False }
                    'content' : 详细内容 list
                    'statues' : 是否预约到 { True | False} 
                    'result' : 结果 str { 预约失败,原因...  | 预约成功,座位号...}
                }

    '''
    if request.method == "GET":

        input_lable = request.GET.get("input_lable",None)

        if input_lable is None:
            resp = {'statue': -2, 'detail': 'Parameter Error'}
            return HttpResponse(json.dumps(resp), content_type="application/json")

        Get_process =  Read_Process_Poll_Value(input_lable)


        if Get_process == None:
            resp = {'statue': -2, 'detail': 'Key Error'}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # 找到
        Result = {
            'complete': Get_process.get('complete',True),
            'content':  Get_process.get('content',[]),
            'statues':  Get_process.get('statues',False),
            'result':   Get_process.get('result','Error'),
        }
        if (Result['result'] == None):
            resp = {'statue': -3, 'content': Result}
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            resp = {'statue': 1, 'content': Result}
            return HttpResponse(json.dumps(resp), content_type="application/json") 

    else:
        resp = {'statue': -1, 'detail': 'Illegal Request'}
        return HttpResponse(json.dumps(resp), content_type="application/json")




# 删除用户
def delete(request):
    username = request.session['username']
    Get_User = User.objects.filter(username = username)
    Get_User.delete()
    del request.session['username']
    return HttpResponseRedirect('/')





# 删除该用户的任务
def delete_assignment(request):
    username = request.session['username']
    weeknum = request.GET.get("weeknum",None)
    if username == None:
        resp = {'statue': -1, 'detail': 'Illegal Request'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    
    if weeknum == None:
        resp = {'statue': -1, 'detail': 'Illegal Request'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    Get_User = User.objects.filter(username = username)
    if len(Get_User) != 1:
        resp = {'statue': -1, 'detail': 'ERROR'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    Get_Assignment = Assignment.objects.filter(User=Get_User[0],Reservation_Day = weeknum).delete()
    resp = {'statue': 1, 'detail': 'success'}
    return HttpResponse(json.dumps(resp), content_type="application/json")
