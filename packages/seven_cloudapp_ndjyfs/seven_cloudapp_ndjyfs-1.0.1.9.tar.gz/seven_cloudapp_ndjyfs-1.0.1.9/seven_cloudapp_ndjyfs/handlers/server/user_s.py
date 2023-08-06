# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-12 20:04:54
:LastEditTime: 2022-02-17 11:30:27
:LastEditors: HuangJingCan
:description: 用户相关
"""

from seven_cloudapp_frame.libs.customize.seven_helper import *

from seven_cloudapp_frame.handlers.frame_base import *

from seven_cloudapp_frame.models.asset_base_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *

from seven_cloudapp_frame.handlers.server.user_s import LoginHandler
from seven_cloudapp_frame.handlers.server.user_s import UpdateUserStatusHandler
from seven_cloudapp_frame.handlers.server.user_s import AssetLogListHandler
from seven_cloudapp_frame.models.asset_base_model import AssetBaseModel

from seven_cloudapp_ndjyfs.models.db_models.user.user_info_ex_model import *


class UserListHandler(ClientBaseHandler):
    """
    :description: 用户列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户列表
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param user_nick：用户昵称
        :param user_state：状态：-1全部0正常1黑名单
        :return PageInfo
        :last_editors: HuangJingCan
        """
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 20)
        act_id = self.get_param_int("act_id")
        user_nick = self.get_param("nick_name")
        user_state = self.get_param_int("user_state", -1)
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")

        act_info = ActInfoModel(context=self).get_dict_by_id(act_id)

        app_id = act_info["app_id"]

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s")

        if user_nick:
            condition.add_condition("user_nick like %s")
            user_nick = f"%{user_nick}%"
            params.append(user_nick)
            # condition.add_condition("user_nick=%s")
            # params.append(user_nick)
        if user_state > -1:
            condition.add_condition("user_state=%s")
            params.append(user_state)
        if create_date_start:
            condition.add_condition("create_date>=%s")
            params.append(create_date_start)
        if create_date_end:
            condition.add_condition("create_date<=%s")
            params.append(create_date_end)

        page_list, total = UserInfoModel(context=self).get_dict_page_list("*", page_index, page_size, condition.to_string(), order_by="create_date desc", params=params)

        if page_list:
            user_ids = str([i["user_id"] for i in page_list]).strip('[').strip(']')
            # 获取用户扩展表
            user_info_ex_list = UserInfoExModel(context=self).get_dict_list(f"user_id IN ({user_ids}) and act_id={act_id}")
            #拼接数据
            user_info_list = SevenHelper.merge_dict_list(user_info_ex_list, "id", page_list, "id")
            user_dict_list = {}
            for user_info in user_info_list:
                user_dict_list[user_info["user_id"]] = user_info
            # 获取积分列表
            user_asset_dict_list = AssetBaseModel(context=self).get_user_asset_list(app_id, act_id, user_ids, 0)

            for user_asset_dict in user_asset_dict_list:
                if user_asset_dict["asset_type"] == 2:
                    user_dict_list[user_asset_dict["user_id"]]["surplus_integral"] = user_asset_dict["asset_value"] if user_asset_dict["asset_value"] else 0
                elif user_asset_dict["asset_type"] == 101:
                    user_dict_list[user_asset_dict["user_id"]]["freight_voucher_value"] = user_asset_dict["asset_value"] if user_asset_dict["asset_value"] else 0

            for user_info in user_info_list:
                if "surplus_integral" not in user_info:
                    user_info["surplus_integral"] = 0
                if "freight_voucher_value" not in user_info:
                    user_info["freight_voucher_value"] = 0

            page_info = PageInfo(page_index, page_size, total, user_info_list)

            return self.response_json_success(page_info)
        else:
            return self.response_json_success(PageInfo(page_index, page_size, total, page_list))


class UpdateUserAssetListHandler(ClientBaseHandler):
    """
    :description: 变更资产
    """
    @filter_check_params("act_id,tb_user_id,asset_update_json,asset_type")
    def post_async(self):
        """
        :description: 变更资产
        :param act_id：活动标识
        :param user_id：用户标识
        :param asset_update_json：资产变更信息
        :param asset_type：资产类型
        :param asset_value：变更的资产值
        :return: response_json_success
        :last_editors: HuangJingCan
        """
        app_id = self.get_app_id()
        act_id = self.get_param_int("act_id")
        tb_user_id = self.get_param_int("tb_user_id")
        asset_update_json = self.json_loads(self.get_param("asset_update_json", '[]'))
        asset_type = self.get_param_int("asset_type")
        # asset_value = int(self.get_param("asset_value", 0))
        # asset_object_id = self.get_param("asset_object_id")

        user_base_model = UserBaseModel(context=self)
        user_info_dict = user_base_model.get_user_info_dict(app_id, act_id, tb_user_id)
        if not user_info_dict:
            return self.response_json_error("error", "用户信息不存在")

        asset_base_model = AssetBaseModel(context=self)
        if len(asset_update_json):
            try:
                for asset_date in asset_update_json:
                    asset_value = asset_date["asset_value"]
                    asset_object_id = asset_date["asset_object_id"]
                    invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, 0, tb_user_id, user_info_dict["open_id"], user_info_dict["user_nick"], asset_type, asset_value, asset_object_id, 3, "", "手动配置", "手动配置")
                    if invoke_result_data.success == False:
                        self.logging_link_error("FailUpdateAsset:" + str(asset_date))
                        return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            except Exception as ex:
                self.logging_link_error("UpdateUserAssetListHandler:" + str(ex))
                return self.response_json_error('ErrorUpdateAssert', '变更异常')
        else:
            return self.response_json_error("ErrorParam", "参数异常")

        return self.response_json_success()


class UserPriceGeartListHandler(ClientBaseHandler):
    """
    :description: 获取用户资产信息
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 获取用户价格档位列表
        :param act_id：活动标识
        :param tb_user_id：用户标识
        # :param asset_type：资产类型(1-次数2-积分3-价格档位101-运费券)
        :return list
        :last_editors: HuangJingCan
        """
        app_id = self.get_app_id()
        act_id = self.get_param_int("act_id")
        user_id = self.get_param_int("tb_user_id")
        asset_type = self.get_param_int("asset_type")
        # asset_type = 3
        asset_base_model = AssetBaseModel(context=self)
        price_gear_model = PriceGearModel(context=self)

        #获取用户资产列表,并处理数据（方便后序调用）
        user_asset_dict = {}
        user_asset_list = asset_base_model.get_user_asset_list(app_id, act_id, user_id, asset_type)

        if asset_type == 3:
            for user_asset in user_asset_list:
                price_gear_id = int(user_asset["asset_object_id"]) if user_asset["asset_object_id"] else 0
                user_asset_dict[price_gear_id] = user_asset

            #获取当前活动价格档位
            price_gear_list = price_gear_model.get_dict_list("act_id=%s AND is_del=0", field="id as price_gear_id,price_gear_name", params=act_id)
            for price_gear in price_gear_list:
                price_gear_id = price_gear["price_gear_id"]
                price_gear["asset_value"] = user_asset_dict[price_gear_id]["asset_value"] if price_gear_id in user_asset_dict else 0
                price_gear["asset_object_id"] = price_gear_id

            return self.response_json_success(price_gear_list)
        else:
            return self.response_json_success(user_asset_list)
