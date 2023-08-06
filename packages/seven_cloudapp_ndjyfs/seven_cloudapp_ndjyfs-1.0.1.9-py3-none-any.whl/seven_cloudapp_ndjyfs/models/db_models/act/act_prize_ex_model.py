# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-20 16:22:36
:LastEditTime: 2022-01-19 17:24:11
:LastEditors: HuangJingCan
:Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import CacheModel


class ActPrizeExModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActPrizeExModel, self).__init__(ActPrizeEx, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类


class ActPrizeEx:
    def __init__(self):
        super(ActPrizeEx, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.ip_id = 0  # ip_id
        self.module_id = 0  # 模块id
        self.module_theme_id = 0  # 机台主题id(关联字段)
        self.act_prize_sku_id = 0  # sku库存表(关联字段)
        self.sale_status = 0  # 发售状态0未发售1已发售
        self.yfs_type = 0  # 一番赏等级类型1普通赏2特殊赏3叠叠乐
        self.yfs_grade = ""  # 一番赏等级
        self.yfs_key_name = ""  # 一番赏识别名称
        self.is_wait_give = 0  # 特殊赏是否满足发赏
        self.first_open_threshold = 0  # First发赏阈值
        self.last_open_threshold = 0  # Last发赏阈值
        self.dd_open_step = 0  # 叠叠赏阶段
        self.dd_open_threshold = 0  # 叠叠赏发赏阈值
        self.is_open_prize_limit = 0  # 是否开启中奖限制
        self.prize_limit = 0  # 中奖限制
        self.is_senior_ability = 0  # 是否开启高级概率
        self.senior_ability_config = ""  # 高级功能配置（List：type_id类型id:1奖品锁定2强制出奖，is_open:是否开启，lock_count:限制数量，unlock_count:解封数量）
        self.is_open_buy_back = 0  # 是否开启回购：0否1是
        self.buy_back_integral = 0  # 回购积分
        self.prize_name = ""  # 奖品名称
        self.prize_title = ""  # 奖品子标题
        self.prize_pic = ""  # 奖品图
        self.prize_detail_json = ""  # 奖品详情json
        self.goods_id = ""  # 商品ID
        self.goods_code = ""  # 商品编码
        self.goods_code_list = ""  # 多个sku商品编码
        self.prize_type = 0  # 奖品类型(1现货2优惠券3红包4参与奖5预售)
        self.prize_price = 0  # 奖品价格
        self.tag_id = 0  # 商品标签(0无1限定2稀有3绝版4隐藏)
        self.probability = 0  # 奖品概率
        self.surplus = 0  # 奖品库存
        self.prize_total = 0  # 奖品总库存
        self.hand_out = 0  # 已发出数量
        self.is_sku = 0  # 是否有SKU
        self.is_release = 0  # 是否发布（1是0否）
        self.is_del = 0  # 是否删除（1是0否）
        self.sku_json = ""  # sku详情json
        self.sort_index = 0  # 排序号
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return [
            'id', 'app_id', 'act_id', 'ip_id', 'module_id', 'module_theme_id', 'act_prize_sku_id', 'sale_status', 'yfs_type', 'yfs_grade', 'yfs_key_name', 'is_wait_give', 'first_open_threshold', 'last_open_threshold', 'dd_open_step', 'dd_open_threshold', 'is_open_prize_limit', 'prize_limit', 'is_senior_ability', 'senior_ability_config', 'is_open_buy_back', 'buy_back_integral', 'prize_name', 'prize_title', 'prize_pic', 'prize_detail_json', 'goods_id', 'goods_code', 'goods_code_list',
            'prize_type', 'prize_price', 'tag_id', 'probability', 'surplus', 'prize_total', 'hand_out', 'is_sku', 'is_release', 'is_del', 'sku_json', 'sort_index', 'create_date', 'modify_date'
        ]

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_prize_ex_tb"
