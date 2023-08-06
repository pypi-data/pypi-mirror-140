# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-26 15:26:32
@LastEditTime: 2022-02-25 17:03:47
@LastEditors: ChenCheng
:Description: 首页信息，活动基础信息
"""
from pymysql import NULL
from seven_cloudapp_frame.handlers.frame_base import *

from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.seven_model import PageInfo
from seven_cloudapp_frame.models.task_base_model import TaskBaseModel

from seven_cloudapp_frame.models.db_models.invite.invite_log_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.theme.theme_info_model import *
from seven_cloudapp_frame.models.db_models.skin.skin_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *
from seven_cloudapp_frame.models.db_models.ip.ip_info_model import *

from seven_cloudapp_ndjyfs.models.enum import *
from seven_cloudapp_ndjyfs.models.business_base_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_info_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_module_ex_model import *


class ActInfoHandler(ClientBaseHandler):
    """
    :description: 前端获取活动信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取活动信息
        :param act_id：活动id
        :return: 字典
        :last_editors: HuangJingCan
        """
        app_id = self.get_source_app_id()
        act_id = self.get_param_int("act_id")

        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.response_json_error("NoApp", "对不起，找不到该小程序")

        act_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        act_dict_ex = ActInfoExModel(context=self).get_dict_by_id(act_id)
        if not act_dict or not act_dict_ex:
            return self.response_json_error("NoAct", "对不起，找不到该活动")
        # 合并扩展表
        act_dict_ex.update(act_dict)
        act_dict = act_dict_ex

        act_dict["seller_id"] = app_info.seller_id
        act_dict["store_id"] = app_info.store_id
        act_dict["store_name"] = app_info.store_name
        act_dict["store_icon"] = app_info.store_icon
        act_dict["app_icon"] = app_info.app_icon
        act_dict["ver_no"] = app_info.template_ver

        # #获取主题信息
        # theme_info_model = ThemeInfoModel(context=self)
        # theme_info = None
        # if act_dict["theme_id"]:
        #     theme_info = theme_info_model.get_dict_by_id(act_dict["theme_id"])
        # if not theme_info:
        #     theme_info = theme_info_model.get_dict(order_by="sort_index")
        # act_dict["theme_info"] = theme_info
        # #获取主题皮肤列表
        # if theme_info:
        #     skin_info_model = SkinInfoModel(context=self)
        #     skin_info_list = skin_info_model.get_dict_list("theme_id=%s", params=[theme_info["id"]])
        #     act_dict["skin_info_list"] = skin_info_list

        act_dict["share_desc_json"] = self.json_loads(act_dict["share_desc_json"])
        act_dict["rule_desc_json"] = self.json_loads(act_dict["rule_desc_json"])
        act_dict["notice_desc_json"] = self.json_loads(act_dict["notice_desc_json"])
        act_dict["carousel_list"] = self.json_loads(act_dict["carousel_list"])

        # 强制关注入会配置（包含判断关注、入会任务是否开启）
        task_base_model = TaskBaseModel(context=self)
        task_info_list = task_base_model.get_task_info_dict_list(app_id, act_id, -1, 1)
        #邀请任务id，0-未开启任务
        act_dict["invite_task_id"] = 0
        #会员任务id，0-未开启任务
        act_dict["membership_task_id"] = 0
        #关注任务id，0-未开启任务
        act_dict["follow_shop_task_id"] = 0
        if task_info_list:
            for task_info in task_info_list:
                task_config = self.json_loads(task_info["config_json"])
                reward_value = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
                if int(task_info["task_type"]) == TaskType.invite_new_user.value:
                    act_dict["invite_task_id"] = task_info["id"]
                    act_dict["invite_task_reward"] = reward_value
                if int(task_info["task_type"]) == TaskType.join_member.value:
                    act_dict["membership_task_id"] = task_info["id"]
                    act_dict["membership_task_reward"] = reward_value
                if int(task_info["task_type"]) == TaskType.favor_store.value:
                    act_dict["follow_shop_task_id"] = task_info["id"]
                    act_dict["follow_shop_task_reward"] = reward_value

        return self.response_json_success(act_dict)


class IpListHandler(ClientBaseHandler):
    """
    :description: IP列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取IP列表
        :param act_id：活动id
        :param ip_type: ip类型(1-现货2预售)
        :param page_index：页索引
        :param page_size：页大小
        :return: list
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        ip_type = self.get_param_int("ip_type", -1)
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s and is_release=1")

        order_by = "sort_index desc"
        if ip_type == -1:
            order_by = "create_date desc"

        if ip_type > 0:
            condition.add_condition("ip_type=%s")
            params.append(ip_type)

        ip_info_model = IpInfoModel(context=self)
        act_prize_ex_model = ActPrizeExModel(context=self)
        act_module_ex_model = ActModuleExModel(context=self)

        # empty_series_list = []  # 售罄系列列表
        # sale_series_list = []  # 在售系列列表

        page_dict_list, total = ip_info_model.get_dict_page_list("*", page_index, page_size, condition.to_string(), "", order_by, params)

        for info in page_dict_list:
            sale_module_id_list = act_prize_ex_model.get_dict_list("ip_id=%s and is_del=0 and is_release=1 and yfs_type=1 and surplus>0", field="DISTINCT module_id", params=info["id"])
            release_module_id_list = act_module_ex_model.get_dict_list("ip_id=%s and is_del=0 and is_release=1", field="id", params=info["id"])

            module_id_list = SevenHelper.merge_dict_list(release_module_id_list, "id", sale_module_id_list, "module_id")
            sale_module_id_list = [i['id'] for i in module_id_list if i.__contains__("module_id") and i['module_id']]

            info["sale_count"] = len(sale_module_id_list)

        page_info = PageInfo(page_index, page_size, total, page_dict_list)

        return self.response_json_success(page_info)


class ActModuleListHandler(ClientBaseHandler):
    """
    :description: 获取机台信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取机台列表
        :param act_id:活动id
        :param price_gear_id:价格挡位id
        :return: 
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        ip_id = self.get_param_int("ip_id")
        price_gear_id = self.get_param_int("price_gear_id")

        act_module_ex_model = ActModuleExModel(context=self)
        price_gear_model = PriceGearModel(context=self)

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s and is_del=0 and is_release=1")

        if ip_id > 0:
            condition.add_condition("ip_id=%s")
            params.append(ip_id)
        if price_gear_id > 0:
            condition.add_condition("price_gear_id=%s")
            params.append(price_gear_id)

        business_base_model = BusinessBaseModel(context=self)
        dependency_key = business_base_model.get_cache_key_act_module_list(act_id)
        machine_info_list = act_module_ex_model.get_cache_dict_list(where=condition.to_string(), order_by="sort_index desc", params=params, dependency_key=dependency_key)
        if len(machine_info_list) > 0:
            price_gear_id_list = list(set([i["price_gear_id"] for i in machine_info_list]))
            price_gear_dict_list_where = SevenHelper.get_condition_by_int_list("id", price_gear_id_list)
            price_gear_dict_list = price_gear_model.get_dict_list(price_gear_dict_list_where, order_by="id desc")
            for machine_info in machine_info_list:
                if machine_info["price_gear_modify_date"] == "1900-01-01 00:00:00":
                    machine_info["price_gear_modify_date"] = ""
                if machine_info["start_date"] == "1900-01-01 00:00:00":
                    machine_info["start_date"] = ""
                if machine_info["end_date"] == "1900-01-01 00:00:00":
                    machine_info["end_date"] = ""
                price_gear_dict = [price_gear_dict for price_gear_dict in price_gear_dict_list if price_gear_dict["id"] == machine_info["price_gear_id"]]
                if len(price_gear_dict) > 0:
                    machine_info["price_gear_info"] = price_gear_dict[0]
                else:
                    machine_info["price_gear_info"] = {}

        return self.response_json_success(machine_info_list)


class PriceGearListHandler(ClientBaseHandler):
    """
    :description: 价格档位列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description:  所有价格档位列表
        :param act_id:活动id
        :param machine_id:机台id
        :return: 
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 500)

        page_dict_list, total = PriceGearModel(context=self).get_dict_page_list("*", page_index, page_size, "act_id=%s and is_del=0", "", "id desc", act_id)
        page_info = PageInfo(page_index, page_size, total, page_dict_list)

        return self.response_json_success(page_info)