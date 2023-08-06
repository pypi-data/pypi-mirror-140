# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-08-03 18:15:30
:LastEditTime: 2022-02-17 10:38:49
:LastEditors: HuangJingCan
:Description: 前端任务相关接口（完成以及奖励）
"""
from seven_cloudapp_frame.handlers.frame_base import *

from seven_cloudapp_frame.handlers.client.theme import *
from seven_cloudapp_frame.models.task_base_model import TaskBaseModel
from seven_cloudapp_frame.models.stat_base_model import StatBaseModel
from seven_cloudapp_frame.models.asset_base_model import AssetBaseModel

from seven_cloudapp_frame.models.db_models.invite.invite_log_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *
from seven_cloudapp_frame.models.db_models.task.task_count_model import *
from seven_cloudapp_frame.models.db_models.task.task_info_model import *

from seven_cloudapp_frame.handlers.client.task import TaskInfoListHandler
from seven_cloudapp_frame.handlers.client.task import WeeklySignHandler
from seven_cloudapp_frame.handlers.client.task import InviteNewUserHandler
from seven_cloudapp_frame.handlers.client.task import JoinMemberHandler
from seven_cloudapp_frame.handlers.client.task import CollectGoodsHandler
from seven_cloudapp_frame.handlers.client.task import BrowseGoodsHandler
from seven_cloudapp_frame.handlers.client.task import FavorStoreHandler
from seven_cloudapp_frame.handlers.client.task import ReceiveRewardHandler

from seven_cloudapp_ndjyfs.models.db_models.user.user_info_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_info_ex_model import *
from seven_cloudapp_ndjyfs.models.enum import *


class TaskInfoListHandler(TaskInfoListHandler):
    """
    :description: 获取任务列表
    """
    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件--消费兑换积分任务 
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: ChenCheng
        """
        act_id = int(self.get_param("act_id", 0))
        user_id = int(self.get_param("tb_user_id", 0))
        task_info_list = ref_params["task_info_list"]
        task_types = self.get_param("task_types")
        user_info_ex_model = UserInfoExModel(context=self)
        result_list = []
        result_data = list(result_data)
        if "201" in task_types:
            user_info_ex = user_info_ex_model.get_dict("act_id=%s and user_id=%s", field="id,store_pay_price", params=[act_id, user_id])
            for task_info in task_info_list:
                config_json = SevenHelper.json_loads(task_info["config_json"])
                if not config_json:
                    continue

                if task_info["task_type"] == TaskType.exchange_integral.value:
                    result = {}
                    result["task_id"] = task_info["id"]
                    result["task_type"] = task_info["task_type"]
                    result["title"] = task_info["task_name"]
                    result["config_json"] = config_json
                    result["reward_value"] = int(config_json["reward_value"]) if config_json.__contains__("reward_value") else 0
                    result["satisfy_num"] = int(config_json["satisfy_num"]) if config_json.__contains__("satisfy_num") else 1
                    result["complete_count"] = user_info_ex["store_pay_price"]
                    result_list.append(result)
                elif result_data and len(result_data):
                    result_list.append(result_data.pop(0))
        else:
            result_list = result_data
        return result_list


class ExchangeIntegralHandler(ClientBaseHandler):
    """
    :description: 消费兑换积分
    """
    @filter_check_params("act_id,tb_user_id,login_token")
    def get_async(self):
        """
        :description: 消费兑换积分
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param tb_user_id:用户标识
        :param login_token:访问令牌
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_source_app_id()
        act_id = self.get_param_int("act_id")
        user_id = self.get_param_int("tb_user_id")
        module_id = self.get_param_int("module_id")
        login_token = self.get_param("login_token")

        invoke_result_data = self.business_process_executing(app_id, act_id, user_id, module_id, login_token)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.process_exchange_integra(app_id, act_id, module_id, user_id, login_token, self.__class__.__name__, self.request_code, invoke_result_data.data["check_user_nick"], invoke_result_data.data["continue_request_expire"])
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        invoke_result_data = self.business_process_executed(invoke_result_data)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)

    def business_process_executing(self, app_id, act_id, user_id, module_id, login_token):
        """
        :description: 执行前事件
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :return:
        :last_editors: HuangJingCan
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"check_user_nick": True, "continue_request_expire": 5, "asset_sub_table": None}
        return invoke_result_data

    def business_process_executed(self, invoke_result_data):
        """
        :description: 执行后事件
        :param invoke_result_data:框架处理结果
        :return:
        :last_editors: HuangJingCan
        """
        return invoke_result_data

    def process_exchange_integra(self, app_id, act_id, module_id, user_id, login_token, handler_name, request_code, check_user_nick=True, continue_request_expire=5, asset_sub_table=None):
        """
        :description: 消费兑换积分任务
        :param app_id:应用标识
        :param act_id:活动标识
        :param module_id:活动模块标识
        :param user_id:用户标识
        :param login_token:访问令牌
        :param handler_name:接口名称
        :param request_code:请求代码
        :param check_user_nick:是否校验昵称为空
        :param continue_request_expire:连续请求过期时间，为0不进行校验，单位秒
        :param asset_sub_table:资产分表名称
        :return 
        :last_editors: HuangJingCan
        """
        acquire_lock_name = f"process_favor_store:{act_id}_{module_id}_{user_id}"
        task_type = TaskType.exchange_integral.value
        now_day = SevenHelper.get_now_day_int()
        now_datetime = SevenHelper.get_now_datetime()
        task_base_model = TaskBaseModel(context=self)
        stat_base_model = StatBaseModel(context=task_base_model.context)
        user_info_ex_model = UserInfoExModel(context=task_base_model.context)
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        try:
            invoke_result_data = task_base_model.business_process_executing(app_id, act_id, module_id, user_id, login_token, handler_name, False, check_user_nick, continue_request_expire, acquire_lock_name)
            if invoke_result_data.success == True:
                act_info_dict = invoke_result_data.data["act_info_dict"]
                user_info_dict = invoke_result_data.data["user_info_dict"]
                user_info_ex_dict = user_info_ex_model.get_dict_by_id(user_info_dict["id"])

                task_invoke_result_data = task_base_model.check_task_info(act_id, module_id, task_type)
                if task_invoke_result_data.success == True:
                    task_info_dict = task_invoke_result_data.data
                    config_json = task_info_dict["config_json"]
                    reward_value = config_json["reward_value"] if config_json.__contains__("reward_value") else 0
                    satisfy_num = config_json["satisfy_num"] if config_json.__contains__("satisfy_num") else 0
                    asset_object_id = config_json["asset_object_id"] if config_json.__contains__("asset_object_id") else ""

                    task_sub_table = SevenHelper.get_sub_table(act_id, config.get_value("task_sub_table_count", 0))
                    task_count_model = TaskCountModel(sub_table=task_sub_table, db_transaction=db_transaction, context=task_base_model.context)
                    task_count_id = task_base_model._get_task_count_id_md5(act_id, module_id, task_type, "", user_id)
                    task_count = task_count_model.get_entity("id_md5=%s", params=task_count_id)
                    task_count = TaskCount() if not task_count else task_count
                    if int(satisfy_num) > float(user_info_ex_dict["store_pay_price"]):
                        invoke_result_data.success = False
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = "兑换金额不足"
                    else:
                        # 更新用户数据
                        if reward_value > 0:
                            # 更新用户积分
                            only_id = task_base_model.get_only_id(user_id, task_info_dict["complete_type"], task_type, "", complete_count=task_count.complete_count)
                            asset_type = task_base_model.get_task_asset_type(act_info_dict["task_asset_type_json"], task_type)
                            asset_base_model = AssetBaseModel(context=task_base_model.context)
                            asset_invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, module_id, user_id, user_info_dict["open_id"], user_info_dict["user_nick"], asset_type, reward_value, asset_object_id, 2, task_type, task_info_dict["task_name"], "消费任务", only_id, handler_name, request_code, info_json={})
                            # 更新用户累计金额
                            # store_pay_price = float(user_info_ex_dict["store_pay_price"]) - int(satisfy_num)
                            user_info_ex_model.update_table("store_pay_price=store_pay_price-%s", "id=%s", params=[int(satisfy_num), user_info_dict['id']])
                            if asset_invoke_result_data.success == False:
                                reward_value = 0
                        # 更新任务完成统计
                        task_count.id_md5 = task_count_id
                        task_count.app_id = app_id
                        task_count.act_id = act_id
                        task_count.module_id = module_id
                        task_count.user_id = user_id
                        task_count.open_id = user_info_dict["open_id"]
                        task_count.task_type = task_type
                        task_count.task_sub_type = ""
                        task_count.complete_count = task_count.complete_count + 1
                        task_count.now_count = 0
                        task_count.create_date = now_datetime
                        task_count.modify_date = now_datetime
                        task_count.modify_day = now_day
                        task_count_model.add_update_entity(task_count, "complete_count=%s,modify_date=%s,modify_day=%s", params=[task_count.complete_count, task_count.modify_date, now_day])
                        # 更新后台数据统计
                        invoke_result_data.data = reward_value
                        if reward_value > 0:
                            key_list_dict = {}
                            key_list_dict["ExchangeUserCount"] = 1  #完成人数
                            key_list_dict["ExchangeCount"] = 1  #完成次数
                            key_list_dict["ExchangeRewardCount"] = reward_value  #奖励值
                            stat_base_model.add_stat_list(app_id, act_id, module_id, user_info_dict["user_id"], user_info_dict["open_id"], key_list_dict)
                else:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = task_invoke_result_data.error_code
                    invoke_result_data.error_message = task_invoke_result_data.error_message

        except Exception as ex:
            task_base_model.context.logging_link_error("【消费兑换任务】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = "系统繁忙,请稍后再试"
        finally:
            self.business_process_executed(invoke_result_data)

        return invoke_result_data