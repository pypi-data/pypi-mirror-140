# -*- coding: utf-8 -*-
"""
@Author: HuangJingCan
@Date: 2021-02-06 15:37:02
:LastEditTime: 2022-01-06 15:21:33
:LastEditors: HuangJingCan
@Description: 
"""

from enum import Enum, unique

class OperationType(Enum):
    """
    :description: 用户操作日志类型
    """
    add = 1 #添加
    update = 2 #更新
    delete = 3 #删除
    review = 4 #还原
    
class ReportDataType(Enum):
    """
    docstring：上报数据类型
    """
    访问数据 = 1
    参与情况 = 2
    销售情况 = 3
    分享数据 = 4


class ActStateType(Enum):
    """
    docstring：活动状态类型
    """
    进行中 = 1
    未开始 = 2
    已完成 = 3


class PrizeSeniorConfigType(Enum):
    """
    docstring：奖品高级配置类型
    """
    奖品锁定 = 1
    强制出奖 = 2

class TaskRelationData(Enum):
    """
    docstring：任务关联数据
    """
    # 每日签到，暂无
    sign = 2
    # 邀请新用户，格式：{"invite_user_id(用户id)":0,"invite_nick_name(用户昵称)":''}
    invite = 3
    # 关注店铺，暂无
    favor = 4
    # 加入店铺会员，暂无
    member = 5
    # 下单购买指定商品，格式：{"main_pay_order_no(淘宝主订单)":'',"tb_order_no(淘宝子订单)":'',"goods_id(商品id)":'',"goods_name(商品名称)":'',"payment(实付金额)":0.00}
    buy = 6
    # 收藏商品，格式：{"goods_id(商品id)":'',"goods_name(商品名称)":''}
    collect = 7
    # 浏览商品，格式：{"goods_id(商品id)":'',"goods_name(商品名称)":''}
    browse = 8

class TaskType(Enum):
    """
    docstring：任务类型
    """
    
    # 邀请新用户，格式：{"reward_value":0,"user_limit":0}
    invite = 3
    # 关注店铺，格式：{"reward_value":0,"isRepeateFavor":1}
    favor = 4
    # 加入店铺会员，格式：{"reward_value":0,"isRepeateMembership":1}
    member = 5
    # 收藏商品，格式：{"reward_value":0,"num_limit":0,"goods_ids":"","goods_list":[]}
    collect = 7
    # 浏览商品，格式：{"reward_value":0,"num_limit":0,"goods_ids":"","goods_list":[]}
    browse = 8
    # 每周签到，格式：{"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
    weekly_sign = 12
    # 消费任务(兑换积分)，格式：{"reward_value":0,"exchange_price":0}
    exchange_integral = 18


class TaskType(Enum):
    """
    docstring：任务类型 业务的自定义任务类型从500起
    """
    # 掌柜有礼、免费领取、新人有礼，格式：{"reward_value":0,,asset_object_id:""}
    free_gift = 1
    # 单次签到，格式：{"reward_value":0,,asset_object_id:""}
    one_sign = 2
    # 每周签到，格式：{day_list:{"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0},asset_object_id:""}
    weekly_sign = 3
    # 邀请新用户，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,asset_object_id:""}
    invite_new_user = 4
    # 邀请入会，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,asset_object_id:""}
    invite_join_member = 5
    # 关注店铺，格式：{"reward_value":0,asset_object_id:""}
    favor_store = 6
    # 加入店铺会员，格式：{"reward_value":0,asset_object_id:""}
    join_member = 7
    # 收藏商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],asset_object_id:""}
    collect_goods = 8
    # 浏览商品，格式：{"reward_value":0,"satisfy_num":1,"limit_num":0,"goods_ids":"","goods_list":[],asset_object_id:""}
    browse_goods = 9
    # 下单指定商品，格式：{"effective_date_start":'1900-01-01 00:00:00',"effective_date_end":'1900-01-01 00:00:00',"reward_value":0,"satisfy_num":0,"limit_num":0,"goods_ids":"","goods_list":[],asset_object_id:""}
    buy_goods = 10
    # 兑换积分任务，格式：{"reward_value":0,"satisfy_num":0}
    exchange_integral  = 201