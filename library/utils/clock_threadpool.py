'''
    描述:这是定时预约的多线程任务
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




def Clock_Upload_Assignment(username,reserve_info):
    # 提交一个异步任务
    future = clock_global_thread_pool.executor.submit(batch_thread, [username,reserve_info])
    clock_global_thread_pool.future_dict[username] = future


def batch_thread(information):
    # 异步任务
    username = information[0]
    reserve_info = information[1]
    from .crawler_clock import Clock_SeatReserve
    try:
        Clock_SeatReserve(reserve_info)
    except Exception as E:
        logger.error("【Clock】异步任务异常\n" + str(reserve_info) + '\n' +traceback.print_exc())
        raise E
    finally:
        # 结束时删除这个任务
        try:
            del clock_global_thread_pool.future_dict[username]
        except Exception as E:
            logger.error("【Clock】异步任务值删除失败"+username)



def Clock_View_futhre():
    # 查看所有的异步任务
    data = clock_global_thread_pool.check_future()
    return data


# 公共变量池
clock_global_thread_pool = ThreadPool()