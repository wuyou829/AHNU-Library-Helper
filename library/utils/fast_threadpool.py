'''
    名称：异步任务线程池
    作用：在快速预约期间，将预约任务交给线程池处理，用户进程直接返回界面,由ajax获取后续更新内容
    备注：这里设定的是公共变量锁
'''
from concurrent.futures.thread import ThreadPoolExecutor
import traceback

import logging
logger = logging.getLogger('collect')


class ThreadPool(object):
    def __init__(self):
        # 线程池
        self.executor = ThreadPoolExecutor(20)

        # 用于存储每个项目批量任务的期程
        self.future_dict = {}



    # 检查某人是否存在正在运行的任务
    def is_project_thread_running(self, username):
        future = self.future_dict.get(username, None)
        if future and future.running():
            # 存在正在运行的批量任务
            return True
        return False

    # 展示所有的异步任务
    def check_future(self):
        data = {}
        for username, future in self.future_dict.items():
            data[username] = future.running()
        return data

    # 关闭
    def __del__(self):
        self.executor.shutdown()




def Upload_Assignment(username,reserve_info):
    # 提交一个异步任务
    future = global_thread_pool.executor.submit(batch_thread, [username,reserve_info])
    global_thread_pool.future_dict[username] = future


def batch_thread(information):
    # 异步任务
    username = information[0]
    reserve_info = information[1]
    from utils.crawler import SeatReserve
    try:
        SeatReserve(reserve_info)
    except Exception as E:
        logger.error("【Fast】异步任务异常\n" + str(reserve_info) + '\n' +traceback.print_exc())
    finally:
        # 结束时删除这个任务
        try:
            del global_thread_pool.future_dict[username]
        except Exception as E:
            logger.error("【Fast】异步任务值删除失败"+username)


def View_futhre():
    # 查看所有的异步任务
    data = global_thread_pool.check_future()
    return data

def Check_futhre(username):
    # 检查异步任务,存在返回True,否则返回False
    return global_thread_pool.is_project_thread_running(username)



# 公共变量池
global_thread_pool = ThreadPool()