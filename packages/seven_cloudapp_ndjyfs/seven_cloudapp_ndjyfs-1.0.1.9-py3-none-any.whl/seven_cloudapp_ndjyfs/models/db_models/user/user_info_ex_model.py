# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-20 16:22:36
:LastEditTime: 2022-01-05 15:36:28
:LastEditors: HuangJingCan
:Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import CacheModel


class UserInfoExModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(UserInfoExModel, self).__init__(UserInfoEx, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类


class UserInfoEx:
    def __init__(self):
        super(UserInfoEx, self).__init__()
        self.id = 0  # id
        self.user_id = 0  # 用户标识
        self.act_id = 0  # act_id
        self.store_pay_price = 0  # 淘宝累计支付金额(任务剩余)
        self.buy_goods_num = 0  # 购买商品数量
        self.price_single_lottery_count = 0  # 价格单抽次数
        self.price_continuous_lottery_count = 0  # 价格连抽次数
        self.integral_single_lottery_count = 0  # 积分单抽次数
        self.integral_continuous_lottery_count = 0  # 积分连抽次数
        self.all_lottery_count = 0  # 全收次数
        self.freight_voucher_value = 0  # 运费券剩余次数
        self.lottery_sum = 0  # 累计出奖数量（不包含特殊赏）
        self.last_order_date = "1900-01-01 00:00:00"  # 订单最后查询时间
        self.relieve_date = "1900-01-01 00:00:00"  # 解禁时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.buy_back_integral = 0  # 回购积分
        self.buy_back_num = 0  # 回购数量

    @classmethod
    def get_field_list(self):
        return ['id', 'user_id', 'act_id', 'store_pay_price', 'buy_goods_num', 'price_single_lottery_count', 'price_continuous_lottery_count', 'integral_single_lottery_count', 'integral_continuous_lottery_count', 'all_lottery_count', 'freight_voucher_value', 'lottery_sum', 'last_order_date', 'relieve_date', 'create_date', 'buy_back_integral', 'buy_back_num']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "user_info_ex_tb"
