from .seat_dict import num_to_name,name_to_num
from .wx_communication import send_message
import requests
import datetime
import json
import time
import random
from .user_setting import user_setting
from .set_process_poll import Change_Process_Poll_Value,Read_Process_Poll_Value
from Core.models import User,QRCode,Signin_Assignment
import traceback
import re
import logging

logger = logging.getLogger('collect')

class Clock_SeatReserve:
    def __init__(self,info_dict):
        # 将预约信息保存
        # TODO 这里添加了info_dict["process_poll_key"]注意调用
        # TODO 建议将快速预约与定时预约分离
        # clock暂时使用的爬虫模块


        self.username = info_dict["username"]                                           # 预约信息用户名
        self.password = info_dict["password"]                                           # 预约信息密码
        self.wxid = info_dict["wxid"]                                                   # 预约信息wxid
        self.seatname = info_dict["seatname"]                                           # 预约信息座位名
        self.seatid = info_dict["seatid"]                                               # 预约信息座位id
        self.push_num = info_dict["push_num"]                                           # 预约信息推进数目
        self.now_count = 0                                                              # 推进计数 
        self.is_auto = info_dict["is_auto"]                                             # 是否自动签到
        self.session = requests.Session()                                               # 登录session
        self.status = 1                                                                 # 登录状态
        self.warninfo = ''                                                             # 微信信息反馈
        self.get_user = info_dict.get("get_user",None) 


        self.really_seatname = ''                                                       # 真正预约到的座位
        if info_dict["is_today"] is True:               
            # 今天              
            self.postdate = str(datetime.date.today())                                  # 预约日期
            self.start_time = self.postdate + " " + info_dict["start_time"]                  # 预约开始时间
            self.end_time = self.postdate + " " +info_dict["end_time"]                       # 预约结束时间
        else:
            # 明天
            self.postdate = str(datetime.date.today() + datetime.timedelta(days=1))
            self.start_time = self.postdate + " " + info_dict["start_time"]
            self.end_time = self.postdate + " " +info_dict["end_time"]



        self.assembly_line()                                                            # 执行预约流水线



    def assembly_line(self):

        # 登录
        self.login()

         # 验证登录
        if self.status == 1:
            # 登录成功

            self.status = -1

            # 执行预约
            self.Run_Seservation()

            # 执行注销
            self.logout()
            


            # 结果判定
            if self.status != 1:
                # 预约不成功
                
                # 反馈结果
                message = "【定时任务】:失败\n创建用户:{0}\n座位:{1}\n日期:{2}\n结果:{3}".format(
                    self.username,
                    self.seatname,
                    self.postdate,
                    self.warninfo
                    )
                send_message(self.wxid,message,True)
            else:
                # 预约成功
        
                # 反馈结果
                message = "【定时预约成功】:\n创建用户:{0}\n==>座位:{1}\n开始时间:{2}\n结束时间:{3}".format(
                    self.username,
                    self.really_seatname,
                    self.start_time,
                    self.end_time
                )
                get_qrcode = QRCode.objects.filter(seatname = self.really_seatname,isable = True)


                try:
                    if len(get_qrcode) != 0:
                        message = message + "\n【自动签到】：签到任务加载成功,签到结果将会在座位开始前1分钟反馈"
                        # 放置签到任务                        
                        valid_time = datetime.datetime.strptime(self.start_time,"%Y-%m-%d %H:%M")
                        creat_signin = Signin_Assignment(
                            User = self.get_user,
                            QRCode = get_qrcode[0],
                            valid_time = valid_time
                            )
                        creat_signin.save()
                    else:
                        message = message + "\n【自动签到】：自动签到任务无法加载,请上传桌面签到二维码(本次任务不能帮您自动签到)"
                except Exception as E:
                    message = message + "\n【自动签到】：签到任务无法完成加载"
                    logger.info(
                        '签到任务失败'+str(E)
                    )
                send_message(self.wxid,message,True)

 
        else:
            # 登录失败

            # 反馈结果
            message = "【定时任务】:失败\n创建用户:{0}\n座位:{1}\n日期:{2}\n结果:{3}".format(
                    self.username,
                    self.seatname,
                    self.postdate,
                    "图书馆账号登录失败:"+str(self.status)
                    )
            send_message(self.wxid,message,True)





    def login(self):
        # 登录操作
        url_login = 'http://libzwxt.ahnu.edu.cn/SeatWx/login.aspx'
        header_login = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        }
        Data_login = {
            '__VIEWSTATE': '/wEPDwULLTE0MTcxNzMyMjZkZAl5GTLNAO7jkaD1B+BbDzJTZe4WiME3RzNDU4obNxXE',
            '__VIEWSTATEGENERATOR': 'F2D227C8',
            '__EVENTVALIDATION': '/wEWBQK1odvtBQLyj/OQAgKXtYSMCgKM54rGBgKj48j5D4sJr7QMZnQ4zS9tzQuQ1arifvSWo1qu0EsBRnWwz6pw',
            'tbUserName': self.username,
            'tbPassWord': self.password,
            'Button1': '登录',
            'hfurl': ''
        }
        try:
            res = self.session.post(url_login, headers=header_login, data=Data_login)
            logger.info(
                    '【clock】登录'+str(Data_login)
                )
            if '个人中心' not in res.text:
                self.status = -1
                self.User.accountenable = False
                self.User.save()

            else:
                self.status = 1

        except Exception as er:
            self.status = -2



    def Run_Seservation(self):
        # 预约操作
        url_seat = 'http://libzwxt.ahnu.edu.cn/SeatWx/ajaxpro/SeatManage.Seat,SeatManage.ashx'
        header_seat = {
            'Host': 'libzwxt.ahnu.edu.cn',
            'Origin': 'http://libzwxt.ahnu.edu.cn',
            'Referer': 'http://libzwxt.ahnu.edu.cn/SeatWx/Seat.aspx?fid=1&sid=2877',
            'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            'X-AjaxPro-Method': 'AddOrder',
        }
        Data_body = {
            "atDate": self.postdate,
            "et": self.end_time,
            "sid": self.seatid,
            "st": self.start_time
        }
        self.now_count = 0


        try:
            while self.now_count < self.push_num:
        
                # 设定爬虫的body
                Data_body['sid'] = self.seatid + self.now_count

                # 计数
                self.now_count += 1

                # 获取对应座位名
                Get_SeatName = num_to_name.get(Data_body['sid'],None)

                # 判定越界
                if Get_SeatName is None:
                    self.warninfo = "向后推进的过程中座位区域发生了变化,终止预约"
                    break

                # 请求包
                res = self.session.post(url_seat, headers=header_seat, data=json.dumps(Data_body))
                logger.info(
                    '【clock】循环判定'+str(Data_body) + '\n' + res.text
                )
                if '成功' not in res.text:
                    # 预约不成功
                    if ("重复" in res.text) or ("冲突" in res.text):
                        self.warninfo = "座位被占"
                        self.status = -1
                    else:
                        self.warninfo = "预约出现其他错误:{0}".format(res.text)
                        self.status = -2
                        break
                else:
                    # 预约成功
                    self.warninfo = "预约成功:您预约到的座位号为:{0}".format(Get_SeatName)
                    self.really_seatname = Get_SeatName
                    self.status = 1
                    break


                # 随机休眠
                time.sleep(int(random.random()*user_setting["random_sleep"]))


        except Exception as e:
            pass


    def logout(self):
        try:
            url_logout = 'https://libzwxt.ahnu.edu.cn/seatwx/LogOut.aspx'
            header_logout = {
                'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            }
            self.session.post(url_logout, headers=header_logout)
            logger.info(
                    '【clock】登出'
                )
        except:
            logger.info(
                    '【clock】登出异常'
                )
