# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-20 16:22:36
:LastEditTime: 2021-12-22 14:00:45
:LastEditors: HuangJingCan
:Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import CacheModel


class ActPrizeSeniorConfigModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActPrizeSeniorConfigModel, self).__init__(ActPrizeSeniorConfig, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ActPrizeSeniorConfig:

    def __init__(self):
        super(ActPrizeSeniorConfig, self).__init__()
        self.id = 0  # 奖品id
        self.prize_id = 0  # 奖品id
        self.app_id = ""  # app_id
        self.act_id = 0  # 活动id
        self.module_id = 0  # 机台id
        self.must_surplus_count = 0  # 必中剩余数（剩余锁定数为0开始计算）
        self.is_lock = 0  # 是否锁定
        self.surplus_lock_count = 0  # 剩余锁定数
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'prize_id', 'app_id', 'act_id', 'module_id', 'must_surplus_count', 'is_lock', 'surplus_lock_count', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_prize_senior_config_tb"
