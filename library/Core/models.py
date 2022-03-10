'''
    描述:本模块描述了数据库,全局数据库都在此模块中定义
    数据库描述

'''
import uuid
from django.db import models




class User(models.Model):
    '''数据库表-User
        本表记录每一个用户的信息
    '''
    username = models.CharField(max_length=64,primary_key=True,blank=False,null=False)  # 图书馆账号
    password = models.CharField(max_length=64,blank=False,null=False)                   # 图书馆密码
    uuid = models.UUIDField(default = uuid.uuid1)                                     # UUID用于微信与图书馆账号绑定
    accountenable = models.BooleanField(default=True)                                   # 图书馆用户是否可用
    wxid = models.CharField(max_length=64,null = True)                                  # WXID
    wxname = models.CharField(max_length=64,null = True)                                # WX名
    wxidenable = models.BooleanField(default=False)                                     # 微信是否可用
    
class Assignment(models.Model):
    '''
        本表记录每一个人的定时任务，每一个人可以有多个任务
        本表为自动增长的主键
    '''
    User = models.ForeignKey(User,on_delete=models.CASCADE)                         # 一对多关系 一个用户可以对应多个任务(联级删除，删除用户时自动删除所有任务)
    seatname = models.CharField(max_length=64,null=True)                            # 座位名称
    sid = models.IntegerField(null=True)                                            # 座位ID   
    Reservation_Day = models.IntegerField(null=True)                                # 座位预约的周几（1~7）
    Run_Day = models.IntegerField(null=True)                                        # 应该周几执行预约（1~7）座位预约的前一天
    begintimestr = models.CharField(max_length=64)                                  # 开始时间范围 HH:MM
    endtimestr = models.CharField(max_length=64)                                    # 结束时间范围 HH:MM

class Fastrecord(models.Model):
    '''
        快速预约记录，用于/Fast/界面显示"历史记录"
    '''
    User = models.ForeignKey(User,on_delete=models.CASCADE)                         # 一对多关系 一个用户可以对应多个任务(联级删除，删除用户时自动删除所有任务)
    seatname = models.CharField(max_length=64,null=True)                            # 座位名称
    sid = models.IntegerField(null=True)                                            # 座位ID   
    begintimestr = models.CharField(max_length=64)                                  # 开始时间 HH:MM
    endtimestr = models.CharField(max_length=64)                                    # 结束时间 HH:MM
    pushnum = models.IntegerField(null=True)                                        # 推进个数
    is_today = models.BooleanField(null=True)                                       # 今天还是明天
    createtime = models.DateTimeField(auto_now_add=True)                            # 生成时间
    auto_reserve = models.BooleanField(default=False)                               # 是否自动签到
    
class QRCode(models.Model):
    '''
        桌面签到二维码,用于用户执行签到
        验证方法
            1. 二维码由/QRCode/页上传
            2. 用户上传时扫描二维码并检验URL合法性
            3. 用户自动签到时,二维码开始验证并判断可用性
            4. 只有ischeck和isable为True二维码才是正确
    '''
    qrcodeurl = models.CharField(max_length=128)                    # 签到二维码本质上是一个URL
    seatname = models.CharField(max_length=64)                      # 签到二维码指向的座位名
    sid = models.IntegerField(null=True)                            # 签到二维码指向的座位号
    ischeck = models.BooleanField(default=False)                    # 二维码是否开始验证
    isable = models.BooleanField(default=False)                     # 二维码是否可用
    uploaduser = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)   # 上传它的用户（用于/qrcode/界面展示上传情况），禁止级联删除
    createtime = models.DateTimeField(auto_now_add=True)            # 上传时间
    img = models.FileField(null=True)                               # 图像

class Signin_Assignment(models.Model):
    '''
        签到任务计划
    '''
    User = models.ForeignKey(User,on_delete=models.CASCADE)                     # 隶属用户
    QRCode = models.ForeignKey(QRCode,on_delete=models.CASCADE)                 # 二维码
    valid_time = models.DateTimeField()                                         # 生效时间
    createtime = models.DateTimeField(auto_now_add=True)                        # 任务创建时间


class Record(models.Model):
    '''
        微信消息记录
    '''
    GetMessageTime = models.DateTimeField(auto_now_add=True)                        # 消息获取时间
    event = models.CharField(max_length=64,null=True)                               # 消息事件
    robot_wxid = models.CharField(max_length=64,null=True)                          # 机器人ID
    robot_name = models.CharField(max_length=64,null=True)                          # 机器人name
    Type = models.CharField(max_length=64,null=True)                                # 消息类型
    from_wxid = models.CharField(max_length=64,null=True)                           # 来源ID（可能有群）
    from_name = models.CharField(max_length=64,null=True)                           # 来源名称
    final_from_wxid = models.CharField(max_length=64,null=True)                     # 来源ID
    final_from_name = models.CharField(max_length=64,null=True)                     # 来源名称
    to_wxid = models.CharField(max_length=64,null=True)                             # 发给某个ID
    msg = models.CharField(max_length=2048,null=True)                               # 消息内容
    message_type_relation = (                                                       
        ('G', 'Get'),
        ('S', 'Send'),
    )
    message_type = models.CharField(max_length=1, choices=message_type_relation)    # 接收信息还是发送信息

class Broadcast(models.Model):
    '''
        用于每一个用户的全员广播消息,在网页中循环轮播
    '''
    GetMessageTime = models.DateTimeField(auto_now_add=True)                    # 广播发送时间
    content = models.CharField(max_length=64,null=True)                         # 广播内容

