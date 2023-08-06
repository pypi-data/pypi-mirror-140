# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-12-24 10:53:51
@LastEditTime: 2022-02-15 11:02:45
@LastEditors: ChenCheng
:Description: 
"""
class BusinessBaseModel():
    """
    :description: 活动信息业务模型
    """
    def __init__(self, context=None):
        self.context = context

    
    def get_prize_type_name(self,prize_type):
        """
        :description: 获取类型名称
        :param prize_type：类型
        :return str
        :last_editors: HuangJingCan
        """
        if prize_type == 2 or prize_type == 3:
            return "优惠券"
        elif prize_type == 4 or prize_type == 6:
            return "参与奖"
        elif prize_type == 5:
            return "预售"
        else:
            return "现货"

    def get_prize_status_name(self, prize_state):
        """
        :description: 获取状态名称
        :param prize_state：类型
        :return str
        :last_editors: HuangJingCan
        """
        if prize_state == 0:
            return "未下单"
        if prize_state == 1:
            return "已下单"
        if prize_state == 2:
            return "已回购"
        return ""

    def get_module_type_unit(self, module_type):
        """
        :description: 获取抽赏模式单位
        :param module_type：类型
        :return str
        :last_editors: HuangJingCan
        """
        if module_type == 1:
            return "元"
        elif module_type == 2:
            return "积分"
        return ""

    def get_module_type_name(self, module_type):
        """
        :description: 获取抽赏模式名称
        :param module_type：类型
        :return str
        :last_editors: HuangJingCan
        """
        if module_type == 1:
            return "次数扭蛋"
        elif module_type == 2:
            return "积分扭蛋"
        elif module_type == 3:
            return "一番赏扭蛋"
        elif module_type == 4:
            return "叠叠乐扭蛋"
        return ""

    def get_sale_status_name(self, sale_status):
        """
        :description: 获取预售状态名称
        :param sale_status：类型
        :return str
        :last_editors: HuangJingCan
        """
        if sale_status == 0:
            return "未发售"
        elif sale_status == 1:
            return "已发售"
        return ""

    def get_yfs_type_name(self, yfs_type):
        """
        :description: 获取奖品等级名称
        :param yfs_type: 奖品等级
        :return str
        :last_editors: HuangJingCan
        """
        if yfs_type == 1:
            return "普通赏"
        elif yfs_type == 2:
            return "特殊赏"
        elif yfs_type == 3:
            return "叠叠乐"
        return ""

    def get_yfs_key_name(self, yfs_grade):
        """
        :description: 获取一番赏识别名称
        :return: list
        :last_editors: HuangJingCan
        """
        if yfs_grade == "末位赏":
            return "End"
        if yfs_grade == "全局赏":
            return "Ovaerall"
        if yfs_grade == "随机赏":
            return "Random"
        if yfs_grade == "冲冲赏":
            return "ChongChong"
        if "叠叠" in yfs_grade:
            return "DD_"+yfs_grade[2:-1]
        return yfs_grade[:-1]

    def get_cache_key_act_module_list(self, act_id):
        """
        :description: 获取缓存key（机台列表）
        :param act_id: 活动id
        :return str
        :last_editors: HuangJingCan
        """
        return f"act_module_list:actid_{act_id}"

    def get_cache_key_act_module(self, module_id):
        """
        :description: 获取缓存key（机台）
        :param act_id: 机台id
        :return str
        :last_editors: HuangJingCan
        """
        return f"act_module:moduleid_{module_id}"

    def get_cache_key_act_info(self, act_id):
        """
        :description: 获取缓存key（活动）
        :param act_id: 活动id
        :return str
        :last_editors: HuangJingCan
        """
        return f"act_info:actid_{act_id}"

    def get_cache_key_act_prize_list_module_id(self, module_id):
        """
        :description: 获取缓存key（奖品列表）
        :param act_id: 机台id
        :return str
        :last_editors: HuangJingCan
        """
        return f"act_prize_list:moduleid_{module_id}"

    def get_cache_key_act_prize_list_act_id(self, act_id):
        """
        :description: 获取缓存key（奖品列表）
        :param act_id: 活动id
        :return str
        :last_editors: HuangJingCan
        """
        return f"act_prize_list:actid_{act_id}"

    def get_cache_key_prize_roster_list(self, act_id):
        """
        :description: 获取缓存key（奖品列表）
        :param act_id: 活动id
        :return str
        :last_editors: HuangJingCan
        """
        return f"prize_roster_list:actid_{act_id}"
    
    def get_cache_key_act_prize_senior_config_list(self, act_id, module_id):
        """
        :description: 获取缓存key（奖品列表）
        :param act_id: 活动id
        :return str
        :last_editors: HuangJingCan
        """
        return f"act_prize_senior_config_list:actid_{act_id}_moduleid_{module_id}"

    def get_cache_key_act_prize_surplus_list(self, module_id):
        """
        :description: 获取缓存key（库存列表）
        :param act_id: 活动id
        :return str
        :last_editors: HuangJingCan
        """
        return f"act_prize_surplus_list:{module_id}"