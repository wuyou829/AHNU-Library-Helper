from django.apps import AppConfig
from utils.user_setting import user_setting
import logging

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Core'
    def ready(Self):
        # 初始化开关
        if user_setting['initialize'] is True:
            from utils.scheduler import Clock_Initialize
            Clock_Initialize()
        
        
        logger = logging.getLogger('collect')
        logger.info(
                    '服务器启动'
                )
