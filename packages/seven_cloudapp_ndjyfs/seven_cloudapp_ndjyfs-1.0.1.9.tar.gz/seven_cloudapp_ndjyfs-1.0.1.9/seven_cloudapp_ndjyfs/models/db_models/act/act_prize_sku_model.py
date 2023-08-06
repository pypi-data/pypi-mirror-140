# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-20 16:22:36
:LastEditTime: 2021-12-21 14:17:44
:LastEditors: HuangJingCan
:Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import CacheModel


class ActPrizeSkuModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActPrizeSkuModel, self).__init__(ActPrizeSku, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类


class ActPrizeSku:
    def __init__(self):
        super(ActPrizeSku, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.act_id = 0  # 活动id
        self.act_prize_id = 0  # 活动奖品id
        self.sku_id = ""  # sku_id
        self.surplus = 0  # 剩余库存
        self.has_out = 0  # 已选择数量
        self.sku_name = ""  # sku属性名称
        self.goods_code = ""  # sku商品编码
        self.is_release = 0  # 是否发布：0未发布1已发布
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['id', 'app_id', 'act_id', 'act_prize_id', 'sku_id', 'surplus', 'has_out', 'sku_name', 'goods_code', 'is_release', 'modify_date', 'create_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_prize_sku_tb"
