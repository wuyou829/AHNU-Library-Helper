from apscheduler.schedulers.background import BackgroundScheduler
from .user_setting import user_setting
from Core.models import Assignment
from Core.models import Signin_Assignment
import datetime
from utils.fast_threadpool import View_futhre
from utils.wx_communication import send_message
from utils.crawler import Run_SignIn
from .crawler_clock import Clock_SeatReserve
from .clock_threadpool import Clock_View_futhre,Clock_Upload_Assignment
from utils.set_process_poll import Clear_Process_Poll,Read_all

import requests
import time
import logging
import traceback

logger = logging.getLogger('collect')

'''
    定时器模块
    1. 定时签到:这是一个可随机增加的定时器
    2. 定时任务:这是一个定时任务的定时器

'''

def Clock_Initialize():
    # 定时器初始化

    # 定时执行预约任务_定时任务执行时间在User_Setting设定
    Timing_Assignment = BackgroundScheduler(timezone="Asia/Shanghai")
    # 定时签到_定时签到扫描时间请在User_Setting设定
    Timing_Signin = BackgroundScheduler(timezone="Asia/Shanghai")
    # 服务器清除公共区缓存
    Timing_Clear = BackgroundScheduler(timezone="Asia/Shanghai")
    # 打印log
    Timing_Log = BackgroundScheduler(timezone="Asia/Shanghai")
    

    
    # misfire_grace_time = 60,coalesce  = True代表任务因卡顿积累后只运行一次以及任务卡顿后出现时间偏差的可执行范围
    Timing_Clear.add_job(Clear_cache,'cron',hour=2, minute = 5,misfire_grace_time = 3600,coalesce  = True)
    Timing_Signin.add_job(Signin_Job,'interval',minutes  = user_setting["signin_scan"])
    Timing_Assignment.add_job(Assignment_Job,'cron',hour=user_setting["assignment_hours"], minute =user_setting["assignment_min"],misfire_grace_time = 3600,coalesce  = True)
    Timing_Log.add_job(Log_Print,'interval', hours=1, misfire_grace_time = 1200,coalesce  = True)


    Timing_Assignment.start()
    Timing_Signin.start()
    Timing_Clear.start()
    Timing_Log.start()

def Log_Print():
    Process_Str = Read_all()
    ThreadPool_Str = str(View_futhre())
    Clock_ThreadPool_Str = str(Clock_View_futhre())
    logger.info("\n【公共变量审查】\n[页面唯一Lable审查]:{0}\n[Fast_Pool]:{1}\n[Clock_Pool]:{2}".format(Process_Str,ThreadPool_Str,Clock_ThreadPool_Str))
    

def Clear_cache():
    # 清空公共缓存区缓存
    try:
        message_str = '执行缓存清除程序'
        send_message(user_setting['admin_wxid'],message_str)
        Clear_Process_Poll()
        message_str = '缓存清理完毕'
        send_message(user_setting['admin_wxid'],message_str)
    except Exception as E:
        message_str = '清理失败'+str(E)
        send_message(user_setting['admin_wxid'],message_str)
    


def Assignment_Job():
    # 循环检验服务器
    Check_Count = 1
    logger.info("【服务器启动检测】开始")
    while Check_Count < 20:
        try:
            message_str = '服务器试探第'+str(Check_Count) + '次'
            send_message(user_setting['admin_wxid'],message_str)

            Check_Count = Check_Count + 1
            url = 'http://libzwxt.ahnu.edu.cn/SeatWx/login.aspx'
            response = requests.get (url)
            if response.status_code == 404:
                logger.info("【服务器启动检测】第{0}次检测失败等待下一次检测".format(str(Check_Count)))
                time.sleep(45)
            else:
                logger.info("【服务器启动检测】第{0}次检测成功开始运行".format(str(Check_Count)))
                Clock_Run()
                break
        except Exception as E:
            logger.info("【服务器启动检测】第{0}次检测失败等待下一次检测:{1}".format(str(Check_Count),str(E)))
            time.sleep(45)
    
    message_str = '定时任务循环结束,下面等待定时任务完成'
    send_message(user_setting['admin_wxid'],message_str)
    for i in range(20):
        time.sleep(30)
        Clock_ThreadPool_Str = Clock_View_futhre()
        run_count = 0
        for key, value in Clock_ThreadPool_Str.items():
            if value is True:
                run_count += 1
        logger.info("【定时任务循环侦测】第{0}次检测,未完成数:{1}".format(str(i),str(run_count)))
    if run_count != 0:
        message_str = '存在10分钟后任务依然没有执行完毕的情况！！！'
        send_message(user_setting['admin_wxid'],message_str)

def Clock_Run():

    # 获取数据库
    now_weeknum = datetime.datetime.now().weekday() + 1

    # 筛选今日运行任务
    get_assignment = Assignment.objects.filter(Run_Day = now_weeknum)

    for item in get_assignment:
        Get_User = item.User
        message_str = "按周预约任务开始运行"
        send_message(Get_User.wxid,message_str)
    
    logger.info("【定时任务】轮询完毕")

    for item in get_assignment:
        # 检测用户
        Get_User = item.User
        if Get_User.wxidenable == False:
            # WXID失效——清除该用户的所有计划
            Assignment.objects.filter(User = Get_User).delete()
            continue

        if Get_User.accountenable == False:
            # 图书馆用户失效——提示
            message_str = "按周预约执行失败\n预约时间:{0}\n原因:图书馆用户失效,请重新登录网站以验证密码".format(["","周一","周二","周三","周四","周五","周六","周日"][item.Reservation_Day])
            send_message(Get_User.wxid,message_str)
            continue


        # 执行预约
        reserve_info = {
                    "username":Get_User.username,
                    "password":Get_User.password,
                    "wxid":Get_User.wxid,
                    "seatname":item.seatname,
                    "seatid":item.sid,
                    "start_time":item.begintimestr,
                    "end_time":item.endtimestr,
                    "is_today":False,
                    "is_auto":True,
                    "push_num":15,
                    "get_user":Get_User,
                }

  
        try:
            Clock_Upload_Assignment(Get_User.username,reserve_info)

            logger.info("【定时任务】{0}执行预约".format(Get_User.username))
        except Exception as E:
            message = ("定时任务执行出错,目前预约结果不定,请自行前往预约网站检查")
            send_message(Get_User.wxid,message)
            logger.info("【定时任务】{0}预约失败:{1}".format(Get_User.username , str(E)))
        finally:
            time.sleep(5)

    




def Signin_Job():
    # 扫描数据库
    get_now_time = datetime.datetime.now().replace(second = 0,microsecond = 0)
    get_now_time = get_now_time + datetime.timedelta(minutes=3)
    get_assignment = Signin_Assignment.objects.filter(valid_time = get_now_time)
    # 检验是否存在执行签到的任务
    for item in get_assignment:
        # 执行签到
        Run_SignIn(item)
        # 反馈结果
        message = "签到任务执行完毕,签到结果本系统不检查,请自行前往官网验证。【https://libzwxt.ahnu.edu.cn/seatwx/】"
        send_message(item.User.wxid,message)

