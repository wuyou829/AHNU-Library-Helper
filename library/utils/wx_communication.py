import json
import requests
import time
import random

from .user_setting import user_setting
'''
    名称:消息发送模块
    功能:
        1.与可爱猫通信，发送消息
'''
def send_message(wxid,message,is_Sleep = False):
    print(message)
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
    }
    postdata = {
        "event":"SendTextMsg",
        "to_wxid":wxid,
        "msg":message,
        "robot_wxid":user_setting["robot_wxid"],
        "group_wxid":"",
        "member_wxid":""
    }
    url = user_setting["WX_url"]
    try:
        if is_Sleep is True:
            time.sleep(random.randint(1,60))        # 防止定时预约时消息突然聚集导致可爱猫宕机
        response = requests.post(url, data=json.dumps(postdata), headers=headers).text
    except:
        print("通讯异常")

