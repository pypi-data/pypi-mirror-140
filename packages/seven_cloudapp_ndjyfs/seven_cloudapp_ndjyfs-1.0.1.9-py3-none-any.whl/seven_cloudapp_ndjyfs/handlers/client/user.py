# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-19 11:33:16
:LastEditTime: 2022-02-17 10:39:04
:LastEditors: HuangJingCan
:description: 用户处理
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.libs.customize.seven_helper import *

from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.models.order_base_model import *
from seven_cloudapp_frame.models.stat_base_model import *

from seven_cloudapp_frame.models.db_models.tao.tao_pay_order_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *

from seven_cloudapp_frame.handlers.client.user import LoginHandler
from seven_cloudapp_frame.handlers.client.user import UpdateUserInfoHandler
from seven_cloudapp_frame.handlers.client.user import UserAssetListHandler
from seven_cloudapp_frame.handlers.client.user import CheckIsMemberHandler
from seven_cloudapp_frame.handlers.client.user import GetJoinMemberUrlHandler
from seven_cloudapp_frame.handlers.client.order import SyncPayOrderHandler

from seven_cloudapp_ndjyfs.models.db_models.user.user_info_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_info_ex_model import *


class LoginHandler(LoginHandler):
    """
    :description: 登录处理
    """
    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: 框架处理结果
        :return:
        :last_editors: HuangJingCan
        """
        app_id = self.get_source_app_id()
        open_id = self.get_param("open_id")
        act_id = self.get_param_int("act_id")
        module_id = self.get_param_int("module_id")
        user_info = result_data.data
        user_id = user_info["user_id"]

        user_info_ex_model = UserInfoExModel(context=self)
        user_info_ex = user_info_ex_model.get_dict_by_id(user_info["id"])
        if not user_info_ex:
            user_info_ex = UserInfoEx()
            user_info_ex.id = user_info["id"]
            user_info_ex.act_id = user_info["act_id"]
            user_info_ex.user_id = user_id
            user_info_ex.create_date = user_info["create_date"]
            user_info_ex_model.add_entity(user_info_ex)
            user_info_ex = user_info_ex.__dict__
        user_info_ex.update(user_info)

        user_info = SevenHelper.merge_dict_list([user_info], "id", [user_info_ex], "id")[0]

        # 补上用户资产
        asset_base_model = AssetBaseModel(context=self)
        user_info["user_asset_list"] = asset_base_model.get_user_asset_list(app_id, act_id, user_id, 0)

        result_data.data = user_info

        # 统计
        stat_base_model = StatBaseModel(context=self)
        key_list_dict = {}
        key_list_dict["VisitCountEveryDay"] = 1
        key_list_dict["VisitManCountEveryDay"] = 1
        key_list_dict["VisitManCountEveryDayIncrease"] = 1
        key_list_dict["TotalVisitManCount"] = 1
        stat_base_model.add_stat_list(app_id, act_id, module_id, user_id, open_id, key_list_dict)

        return result_data