# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-20 16:22:36
@LastEditTime: 2022-02-16 17:05:00
@LastEditors: ChenCheng
:Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import CacheModel


class ActModuleExModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActModuleExModel, self).__init__(ActModuleEx, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类


class ActModuleEx:
    def __init__(self):
        super(ActModuleEx, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # 应用标识
        self.act_id = 0  # act_id
        self.sort_index = 0  # 排序
        self.ip_id = 0  # IP主题id
        self.module_name = ""  # 机台名称
        self.skin_id = 0  # 皮肤id
        self.module_pic = ""  # 模块图片
        self.module_desc = ""  # 描述信息
        self.module_type = 0  # 抽赏模式:1次数2积分3一番赏4叠叠赏
        self.price_gear_id = 0  # 价格档位id
        self.price_gear_modify_date = "1900-01-01 00:00:00"  # 最后修改价格档位id时间
        self.single_lottery_price = 0  # 单抽（价格档位）价格
        self.continuous_lottery_times = 0  # 连抽次数
        self.single_lottery_integral = 0  # 单抽积分
        self.continuous_lottery_integral = 0  # 连抽积分
        self.continuous_lottery_integral_times = 0  # 连抽积分次数
        self.is_limit_lottery_times = 0  # 是否限制扭蛋次数(0-不限制1限制)
        self.single_lottery_limit = 0  # 单抽每日限制次数
        self.continuous_lottery_limit = 0  # 连抽每日限制次数
        self.is_open_all_lottery = 0  # 是否开启全收（0-未开启1-开启）
        self.all_lottery_count = 0  # 全收数量
        self.is_no_repeat_prize = 0  # 连抽奖品不重复：0-重复1-不重复
        self.is_automatic_buy_back = 0  # 是否开启自动回购0关闭1开启
        self.automatic_buy_back_days = 0  # 自动回购天数
        self.is_surplus = 1  # 是否显示奖品库存：0-不显示1-显示
        self.is_chance = 1  # 是否显示奖品概率：0-不显示1-显示
        self.is_notice = 1  # 是否显示机台中奖弹幕：0-不显示1-显示
        self.start_date = "1900-01-01 00:00:00"  # 开始销售时间
        self.end_date = "1900-01-01 00:00:00"  # 结束销售时间
        self.is_release = 0  # 是否发布：1发布0-未发布
        self.is_del = 0  # 是否删除（1是0否）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return [
            'id', 'app_id', 'act_id', 'sort_index', 'ip_id', 'module_name', 'skin_id', 'module_pic', 'module_desc', 'module_type', 'price_gear_id', 'price_gear_modify_date', 'single_lottery_price', 'continuous_lottery_times', 'single_lottery_integral', 'continuous_lottery_integral', 'continuous_lottery_integral_times', 'is_limit_lottery_times', 'single_lottery_limit', 'continuous_lottery_limit', 'is_open_all_lottery', 'all_lottery_count', 'is_no_repeat_prize', 'is_automatic_buy_back',
            'automatic_buy_back_days', 'is_surplus', 'is_chance', 'is_notice', 'start_date', 'end_date', 'is_release', 'is_del', 'create_date', 'modify_date'
        ]

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_module_ex_tb"
