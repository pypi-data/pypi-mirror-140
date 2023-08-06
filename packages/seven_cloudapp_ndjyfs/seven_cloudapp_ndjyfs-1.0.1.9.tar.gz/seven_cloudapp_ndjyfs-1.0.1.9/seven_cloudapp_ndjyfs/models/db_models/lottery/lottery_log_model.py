# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-20 16:23:12
:LastEditTime: 2021-12-21 14:18:04
:LastEditors: HuangJingCan
:Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import CacheModel


class LotteryLogModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(LotteryLogModel, self).__init__(LotteryLog, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class LotteryLog:

    def __init__(self):
        super(LotteryLog, self).__init__()
        self.id = 0  # id
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户id
        self.module_id = 0  # 机台id
        self.button_num = 0  # 按钮编号
        self.button_count = 0  # 单日按钮数量
        self.create_day = 0  # 创建天
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'act_id', 'user_id', 'module_id', 'button_num', 'button_count', 'create_day', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "lottery_log_tb"
