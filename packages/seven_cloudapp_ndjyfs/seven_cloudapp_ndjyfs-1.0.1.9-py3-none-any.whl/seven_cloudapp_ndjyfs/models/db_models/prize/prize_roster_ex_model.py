# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-20 16:22:36
:LastEditTime: 2022-01-19 17:24:30
:LastEditors: HuangJingCan
:Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import CacheModel


class PrizeRosterExModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PrizeRosterExModel, self).__init__(PrizeRosterEx, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类


class PrizeRosterEx:
    def __init__(self):
        super(PrizeRosterEx, self).__init__()
        self.id = 0  # 标识
        self.app_id = ""  # 应用标识
        self.act_id = 0  # 活动标识
        self.user_id = 0  # 用户id
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户名
        self.ip_id = 0  # ip_id
        self.module_id = 0  # module_id
        self.module_type = 0  # 抽赏模式:1次数2积分3一番赏4叠叠赏
        self.module_name = ""  # module名称
        self.module_price = 0  # module价值
        self.order_no = ""  # 订单号
        self.source_type = 0  # 来源类型（0-活动奖品1-任务奖品2-兑换奖品）业务自定义从101开始
        self.source_object_id = ""  # 来源对象标识
        self.prize_order_id = 0  # 奖品订单id
        self.price_gear_id = 0  # 价格档位id
        self.serial_num = 0  # 行为编号
        self.sale_status = 0  # 发售状态0未发售1已发售
        self.asset_type = 0  # 资产类型:2积分3价格档位
        self.yfs_type = 0  # 一番赏等级类型1普通2特殊
        self.yfs_grade = ""  # 番赏等级
        self.yfs_key_name = ""  # 一番赏识别名称
        self.is_open_buy_back = 0  # 是否开启回购：0否1是
        self.buy_back_integral = 0  # 回购积分
        self.is_automatic_buy_back = 0  # 是否开启自动回购0关闭1开启
        self.automatic_buy_back_days = 0  # 自动回购天数
        self.automatic_buy_back_start_date = "1900-01-01 00:00:00"  # 自动回购开始计算时间
        self.automatic_buy_back_end_date = "1900-01-01 00:00:00"  # 自动回购结束时间
        self.buy_back_date = "1900-01-01 00:00:00"  # 回购时间
        self.prize_id = 0  # 奖品标识
        self.prize_type = 0  # 奖品类型(1现货2优惠券3红包4参与奖5预售)
        self.prize_name = ""  # 奖品名称
        self.prize_title = ""  # 奖品子标题
        self.prize_pic = ""  # 奖品图
        self.prize_detail_json = ""  # 奖品详情json
        self.prize_price = 0  # 奖品价格
        self.tag_id = 0  # 商品标签(0无1限定2稀有3绝版4隐藏)
        self.logistics_status = 0  # 物流状态（0未发货1已发货2不予发货）
        self.prize_status = 0  # 奖品状态：0未下单（未领取）1已下单（已领取）2已回购10已隐藏（删除）11无需发货
        self.pay_status = 0  # 支付状态(0未支付1已支付2已退款3处理中)
        self.goods_id = ""  # 商品ID
        self.goods_code = ""  # 商品编码
        self.goods_code_list = ""  # 多个sku商品编码
        self.is_sku = 0  # 是否有SKU
        self.sku_id = ""  # sku_id
        self.sku_name = ""  # sku_name
        self.sku_json = ""  # sku详情json
        self.main_pay_order_no = ""  # 支付主订单号
        self.sub_pay_order_no = ""  # 支付子订单号
        self.have_presale_prize_notice = 0  # 预售奖品开售是否已经通知
        self.have_special_prize_notice = 0  # 特殊奖品发放是否已经通知
        self.request_code = ""  # 请求代码
        self.is_del = 0  # 是否删除（1是0否）
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return [
            'id', 'app_id', 'act_id', 'user_id', 'open_id', 'user_nick', 'ip_id', 'module_id', 'module_type', 'module_name', 'module_price', 'order_no', 'source_type', 'source_object_id', 'prize_order_id', 'price_gear_id', 'serial_num', 'sale_status', 'asset_type', 'yfs_type', 'yfs_grade', 'yfs_key_name', 'is_open_buy_back', 'buy_back_integral', 'is_automatic_buy_back', 'automatic_buy_back_days', 'automatic_buy_back_start_date', 'automatic_buy_back_end_date', 'buy_back_date', 'prize_id',
            'prize_type', 'prize_name', 'prize_title', 'prize_pic', 'prize_detail_json', 'prize_price', 'tag_id', 'logistics_status', 'prize_status', 'pay_status', 'goods_id', 'goods_code', 'goods_code_list', 'is_sku', 'sku_id', 'sku_name', 'sku_json', 'main_pay_order_no', 'sub_pay_order_no', 'have_presale_prize_notice', 'have_special_prize_notice', 'request_code', 'is_del', 'modify_date', 'create_date'
        ]

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "prize_roster_ex_tb"
