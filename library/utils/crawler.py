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

'''
    功能：快速预约座位
    功能详情：
        1. Fast调用本模块
        2. 本模块进行预约 
'''


class SeatReserve:
    def __init__(self,info_dict):
        # 将预约信息保存
        # TODO 这里添加了info_dict["process_poll_key"]注意调用
        # TODO 建议将快速预约与定时预约分离

        self.username = info_dict["username"]                                           # 预约信息用户名
        self.password = info_dict["password"]                                           # 预约信息密码
        self.wxid = info_dict["wxid"]                                                   # 预约信息wxid
        self.seatname = info_dict["seatname"]                                           # 预约信息座位名
        self.seatid = info_dict["seatid"]                                               # 预约信息座位id
        self.push_num = info_dict["push_num"]                                           # 预约信息推进数目
        self.now_count = 0                                                              # 推进计数 
        self.is_auto = info_dict["is_auto"]                                             # 是否自动签到
        self.process_poll_key = info_dict["process_poll_key"]                           # 状态字典索引

        self.session = requests.Session()                                               # 登录session
        self.status = 1                                                                 # 登录状态
        self.infolog = ["任务创建"]                                                  # 预约日志
        self.wxmessage = ''                                                             # 向微信发送的信息       


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
        # 获取用户微信状态
        get_user = User.objects.filter(username = self.username)


        if( len(get_user) != 1 ):
            # 图书馆用户不存在
            Change_Process_Poll_Value(
                    self.process_poll_key,
                    self.username,
                    True,
                    self.infolog,
                    False,
                    "图书馆账号异常"
                )
            self.infolog.append("图书馆账号异常")
            self.wxmessage = "图书馆账号异常"
            return None



        get_user = get_user[0]
        wxidenable = get_user.wxidenable        # 是否关联微信账号

        # 微信——发送任务的消息
        message = "创建任务:\n座位:{0}\n用户:{1}\n创建时间:{2}\n开始时间:{3}\n结束时间:{4}\n\n".format(
            self.seatname,
            self.username,
            Read_Process_Poll_Value(self.process_poll_key,'creattime').strftime("%m/%d %H:%M"),
            self.start_time,
            self.end_time
            )
        if (wxidenable is False) and (self.is_auto is True):
            self.infolog.append("您没有绑定微信用户,自动签到功能将不会生效。")
            
        # 登录
        self.login()
        
         # 验证登录
        if self.status == 1:
            # 登录成功
            # 设定状态变量
            Change_Process_Poll_Value(
                    self.process_poll_key,
                    self.username,
                    False,
                    self.infolog,
                    False,
                    ""
            )

            self.status = -1
        
            # 执行预约
            self.Run_Seservation()

            # 执行注销
            self.logout()
            

            # 结果判定
            if self.status != 1:
                # 预约不成功
                
                # 设定公共变量
                Change_Process_Poll_Value(
                    self.process_poll_key,
                    self.username,
                    True,
                    self.infolog,
                    False,
                    "预约失败"
                )


                # 反馈结果
                message = message + "=> 快速预约失败 <= \n详情:{0}".format(
                    self.wxmessage
                    )
                if wxidenable:
                    send_message(self.wxid,message)
            else:
                # 预约成功
                
                # 设定公共变量
                Change_Process_Poll_Value(
                    self.process_poll_key,
                    self.username,
                    True,
                    self.infolog,
                    True,
                    "预约成功"
                )


                # 反馈结果
                message = message + "=> 预约成功 <= \n=> 实际座位:{0}".format(
                    self.really_seatname
                    )


                # 发送消息,放置自动签到任务
                if wxidenable:
                    # 自动签到
                    if self.is_auto:
                        # 检查签到二维码状态，反馈到网页
                        get_qrcode = QRCode.objects.filter(seatname = self.really_seatname,isable = True)
                        if len(get_qrcode) != 0:
                            self.infolog.append("当前座位支持签到,工具将在座位预约的开始时间自动签到,签到结果请关注微信")
                            message = message + "\n签到情况:当前座位支持签到,请在开始时间关注签到结果(请注意签到反馈,有几率签到失败)"
                            # 放置签到任务                        
                            valid_time = datetime.datetime.strptime(self.start_time,"%Y-%m-%d %H:%M")
                            creat_signin = Signin_Assignment(
                                User = get_user,
                                QRCode = get_qrcode[0],
                                valid_time = valid_time
                            )

                            creat_signin.save()
                        else:
                            self.infolog.append("服务器中没有该座位的签到二维码,无法为您自动签到,请先上传桌面二维码。")
                            message = message + "\n服务器中没有该座位的签到二维码,无法为您自动签到,请先上传桌面二维码。"


                    # 发送反馈-wx
                    send_message(self.wxid,message)
        else:
            # 登录失败
            # 设定状态变量
            Change_Process_Poll_Value(
                self.process_poll_key,
                self.username,
                True,
                self.infolog,
                False,
                "图书馆账号登录失败"
            )

            # 反馈结果
            message = message + "任务结果反馈:\n创建时间:{0}\n创建用户:{1}\n座位:{2}\n结果:{3}".format(
                    Read_Process_Poll_Value(self.process_poll_key,'creattime').strftime("%m/%d %H:%M"),
                    self.username,
                    self.seatname,
                    "图书馆账号登录失败"
                    )


            if wxidenable:
                send_message(self.wxid,message)



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
                    '【fast】登入'+str(Data_login)
                )
            if '个人中心' not in res.text:
                self.status = -1
                self.infolog.append("登录失败")
                self.infolog.append("程序终止")

            else:
                self.status = 1
                self.infolog.append("登录成功")

        except Exception as er:


            self.status = -1
            self.infolog.append("爬虫模块异常,请重试,如果多次出现请联系开发者:" +  str(repr(e)))
            self.infolog.append("程序终止")


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
        
                # 修改状态
                Change_Process_Poll_Value(
                    self.process_poll_key,
                    self.username,
                    False,
                    self.infolog,
                    False,
                    "正在预约"
                )


                # 设定爬虫的body
                Data_body['sid'] = self.seatid + self.now_count

                # 计数
                self.now_count += 1

                # 获取对应座位名
                Get_SeatName = num_to_name.get(Data_body['sid'],None)

                # 判定越界
                if Get_SeatName is None:
                    self.infolog.append("向后推进的过程中座位区域发生了变化,终止预约")
                    self.wxmessage = "向后推进的过程中座位区域发生了变化,终止预约"
                    break

                # 请求包
                res = self.session.post(url_seat, headers=header_seat, data=json.dumps(Data_body))

                logger.info(
                    "【Fast】循环判定" + str(Data_body) + '\n' + res.text
                )

                if '成功' not in res.text:
                    # 预约不成功
                    if ("重复" in res.text) or ("冲突" in res.text):
                        self.infolog.append("{0}-座位被占".format(Get_SeatName))
                        self.wxmessage = "座位被占"
                        self.status = -1
                    else:
                        self.infolog.append("其他错误:{0}".format(res.text))
                        self.wxmessage = "预约出现错误:{0}".format(res.text)
                        self.status = -2
                        break
                else:
                    # 预约成功
                    self.infolog.append("预约成功:您预约到的座位号为:{0}".format(Get_SeatName))
                    self.wxmessage = "预约成功:您预约到的座位号为:{0}".format(Get_SeatName)
                    self.really_seatname = Get_SeatName
                    self.status = 1
                    
                    break


                # 随机休眠
                time.sleep(int(random.random()*user_setting["random_sleep"]))


        except Exception as e:
            self.infolog.append("程序抛出错误\n" + str(repr(e)))


    def logout(self):
        try:
            url_logout = 'https://libzwxt.ahnu.edu.cn/seatwx/LogOut.aspx'
            header_logout = {
                'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            }
            self.session.post(url_logout, headers=header_logout)
            logger.info(
                    '【fast】登出'
                )
        except:
            self.infolog.append("登出失败")


class QRCode_Check:
    def __init__(self,QRCode,URL):
        self.User = QRCode.uploaduser
        self.QRCode = QRCode
        self.username = self.User.username
        self.password = self.User.password
        self.infolog = ""
        self.status = -1
        self.session = requests.Session()
        self.QRCodeUrl = URL
    
    def Run(self):
        # 检查数据库
        Get_QRCode = QRCode.objects.filter(qrcodeurl = self.QRCodeUrl,isable = True)
        if len(Get_QRCode) != 0:
            self.QRCode.qrcodeurl = self.QRCodeUrl
            self.QRCode.seatname = Get_QRCode[0].seatname
            self.QRCode.sid = Get_QRCode[0].sid
            self.QRCode.ischeck = True
            self.QRCode.isable = False
            self.QRCode.img = None
            self.QRCode.save()
            return '存在签到二维码'

        else:
            self.login()
            if self.status == -1:
                return self.infolog
            result = self.Check()
            return result


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
                    '【QRCode】登入'+str(Data_login)
                )
            if '个人中心' not in res.text:
                self.status = -1
                self.infolog = "登录失败,请检查密码."
                
            else:
                self.status = 1
                self.infolog = "登录成功"

        except Exception as er:
            self.status = -1
            self.infolog = "Request请求异常:" +  str(repr(e))

    def Check(self):
        # 检查URL
        # self.QRCodeUrl
        header_login = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        }
        try:
            res = self.session.post(self.QRCodeUrl, headers=header_login,timeout = 5)
            logger.info(
                    '【QRCode】检查'
                )
            Pa = r'<header>(.*)</header>'
            Get_info = re.findall(Pa,res.text)[0]
            SeatName = Get_info.split('-')[-1]
            SeatId = name_to_num.get(SeatName,None)
            if SeatId == None:
                raise ValueError("解析错误")
            self.QRCode.qrcodeurl = self.QRCodeUrl
            self.QRCode.seatname = SeatName
            self.QRCode.sid = SeatId
            self.QRCode.ischeck = True
            self.QRCode.isable = True
            self.QRCode.img = None
            self.QRCode.save()
            return "上传成功"

        except Exception as e:
            self.QRCode.delete()
            return "图书馆系统网络请求失败"


class Run_SignIn:


    def __init__(self,Assignment_Info):
        self.info = Assignment_Info
        self.status = -1
        self.infolog = ''
        self.session = requests.Session()
        self.Run()

    def Run(self):
        self.login()
        self.access()
        self.check()

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
            'tbUserName': self.info.User.username,
            'tbPassWord': self.info.User.password,
            'Button1': '登录',
            'hfurl': ''
        }
        try:
            res = self.session.post(url_login, headers=header_login, data=Data_login)
            logger.info(
                    '【SignIn】登入'+str(Data_login)
                )
            if '个人中心' not in res.text:
                self.status = -1
                self.infolog = "登录失败"
            else:
                self.status = 1
                self.infolog = "登录成功"

        except Exception as er:
            self.status = -1
            self.infolog = "Request请求异常:" +  str(repr(e))

    def access(self):
        # 访问
        sign_url = self.info.QRCode.qrcodeurl
        header_login = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        }
        res = self.session.post(sign_url, headers=header_login)
        logger.info(
                    '【SignIn】验证'
                )
        

    def check(self):
    # 检验签到结果
        print("签到结果检验")

 
def Account_Valid(username,password):
    '''
        功能：用户密码验证程序,在用户登录的过程中调用并验证密码
        参数：用户名与密码
        返回值：账号验证结果
    '''
    url_login = 'http://libzwxt.ahnu.edu.cn/SeatWx/login.aspx'
    url_logout = 'https://libzwxt.ahnu.edu.cn/seatwx/LogOut.aspx'
    header_login = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        }
    Data_login = {
            '__VIEWSTATE': '/wEPDwULLTE0MTcxNzMyMjZkZAl5GTLNAO7jkaD1B+BbDzJTZe4WiME3RzNDU4obNxXE',
            '__VIEWSTATEGENERATOR': 'F2D227C8',
            '__EVENTVALIDATION': '/wEWBQK1odvtBQLyj/OQAgKXtYSMCgKM54rGBgKj48j5D4sJr7QMZnQ4zS9tzQuQ1arifvSWo1qu0EsBRnWwz6pw',
            'tbUserName': username,
            'tbPassWord': password,
            'Button1': '登录',
            'hfurl': ''
        }
    sess = requests.Session()
    res = sess.post(url_login, headers=header_login, data=Data_login)
    logger.info(
                    '【Account】登入'+str(Data_login)
                )
    if res.status_code == 404:
        Get_User = User.objects.filter(username = username,password = password)
        if len(Get_User) == 1:
            return True
        else:
            raise ValueError("404 not found!")
        
    if '个人中心' not in res.text:
        status = False
    else:
        status = True
        res = sess.post(url_logout, headers=header_login)
    return status







    # 完成签到