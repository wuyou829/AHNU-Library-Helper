from Core.models import Record

''' 
    名称：微信聊天数据记录数据库模块
    功能：记录接收和发送的详情到数据库
'''
def message_recording(body_dict):    
    ''' 
    作用：数据库记录接收到的信息到数据库,并且返回一个整理好的字典格式
    调用：在Core.Views.py中引用,当django接收到一个微信消息的时候调用
    接收到的微信消息格式：
        {
	        'event': 'EventFriendMsg',
	        'robot_wxid': 'wxid_sl********9x22',
	        'robot_name': '',
	        'type': 1,
	        'from_wxid': '',
	        'from_name': '',
	        'final_from_wxid': 'wxid_5n********k22',
	        'final_from_name': 'S**w',
	        'to_wxid': 'wxid_sln********x22',
	        'msg': '测试'
        }
    本函数返回格式:
        {
	        'robotwxid': 'wxid_sl********9x22',
	        'wxid': 'wxid_5n********k22',
	        'wxname': 'S**w',
	        'message': '测试'
        }
    '''
    CreatNote = Record(                                     # 记录消息
            event = body_dict['event'],
            robot_wxid = body_dict['robot_wxid'],
            robot_name = body_dict['robot_name'],
            Type = body_dict['type'],
            from_wxid = body_dict['from_wxid'],
            from_name = body_dict['from_name'],
            final_from_wxid = body_dict['final_from_wxid'],
            final_from_name = body_dict['final_from_name'],
            to_wxid = body_dict['to_wxid'],
            msg = body_dict['msg'],
            message_type = "G"
        )
    return_dict = {
        'robotwxid':body_dict['robot_wxid'],
        'wxid':body_dict['final_from_wxid'],
        'wxname':body_dict['final_from_name'],
        'message':str(body_dict['msg'])                 # 测试发现当message为纯数字时为int类型
    }
    CreatNote.save()
    return return_dict