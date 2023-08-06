# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-20 16:22:36
:LastEditTime: 2021-12-22 15:50:34
:LastEditors: HuangJingCan
:Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import CacheModel


class ActInfoExModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActInfoExModel, self).__init__(ActInfoEx, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类


class ActInfoEx:
    def __init__(self):
        super(ActInfoEx, self).__init__()
        self.id = 0  #
        self.act_id = 0  # act_id
        self.is_open_buy_back = 0  # 是否开启回购
        self.step_configured = 0  # 已配置步骤
        self.carousel_list = ""  # 首页轮播配置
        self.notice_desc_json = ""  # 公告内容
        self.is_del = 0  # 是否删除（1是0否）
        self.is_release = 0  # 是否发布（1是0否）
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.is_collection_shop_tips = 0  # 是否收藏提醒：0否1是
        self.collection_tips_type = 0  # 收藏提示类型：1小程序启动时2抽奖时
        self.is_force_collection = 0  # 是否强制收藏：0否1是
        self.is_membership_tips = 0  # 是否加入会员提醒：0否1是
        self.membership_tips_type = 0  # 加入会员提示类型：1小程序启动时2抽奖时
        self.is_force_membership = 0  # 是否强制加入会员：0否1是
        self.freight_goods_id = ""  # 运费关联ID
        self.freight_price = 0  # 运费券价格
        self.freight_statement = ""  # 发货内页说明
        self.is_open_freight_free_num = 0  # 是否开启满数量包邮
        self.freight_free_num = 0  # 满数量包邮件数
        self.is_open_freight_free_price = 0  # 是否开启满金额包邮
        self.freight_free_price = 0  # 满金额包邮金额
        self.is_freight_free = 0  # 是否无条件包邮，0否1是
        self.freight_free_start_date = "1900-01-01 00:00:00"  # 包邮活动开始时间
        self.freight_free_end_date = "1900-01-01 00:00:00"  # 包邮活动结束时间

    @classmethod
    def get_field_list(self):
        return [
            'id', 'act_id', 'is_open_buy_back', 'step_configured', 'carousel_list', 'notice_desc_json', 'is_del', 'is_release', 'create_date', 'modify_date', 'is_collection_shop_tips', 'collection_tips_type', 'is_force_collection', 'is_membership_tips', 'membership_tips_type', 'is_force_membership', 'freight_goods_id', 'freight_price', 'freight_statement', 'is_open_freight_free_num', 'freight_free_num', 'is_open_freight_free_price', 'freight_free_price', 'is_freight_free',
            'freight_free_start_date', 'freight_free_end_date'
        ]

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_info_ex_tb"
