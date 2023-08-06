# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-08-04 16:24:18
@LastEditTime: 2022-02-23 14:02:51
@LastEditors: ChenCheng
:description: IP相关
"""
from seven_cloudapp_frame.handlers.frame_base import *

from seven_cloudapp_frame.handlers.server.ip_s import IpInfoListHandler
from seven_cloudapp_frame.handlers.server.ip_s import SaveIpInfoHandler
from seven_cloudapp_frame.handlers.server.ip_s import ReleaseIpInfoHandler
from seven_cloudapp_frame.handlers.server.ip_s import DeleteIpInfoHandler

from seven_cloudapp_ndjyfs.models.db_models.act.act_module_ex_model import *

from seven_cloudapp_ndjyfs.models.business_base_model import *


class IpInfoListHandler(IpInfoListHandler):
    """
    :description: IP列表
    """
    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        app_id = self.get_param("app_id")
        for info in result_data:
            info["ip_url"] = self.get_online_url(act_id, app_id) + "," + str(info["id"])

        return result_data


# class ReleaseIpInfoHandler(ReleaseIpInfoHandler):
#     """
#     :description: 上下架IP
#     """
#     def business_process_executing(self):
#         """
#         :description: 执行前事件
#         :param
#         :return: InvokeResultData
#         :last_editors: HuangJingCan
#         """
#         ip_id = self.get_param_int("ip_id")
#         invoke_result_data = InvokeResultData()

#         act_module_model = ActModuleExModel(context=self)
#         info_dict = act_module_model.get_dict("ip_id=%s and is_release=1", params=[ip_id])
#         if info_dict:
#             invoke_result_data.success = False
#             invoke_result_data.error_code = "popup_error"
#             invoke_result_data.error_message = "当前主题下绑定的机台为发布状态，无法下架，需先下架该主题下所属的机台才可操作"
#             return invoke_result_data

#         return invoke_result_data


class DeleteIpInfoHandler(DeleteIpInfoHandler):
    """
    :description: 删除IP
    """
    def business_process_executing(self):
        """
        :description: 执行前事件
        :param 
        :return: InvokeResultData
        :last_editors: HuangJingCan
        """
        ip_id = self.get_param_int("ip_id")
        invoke_result_data = InvokeResultData()

        act_module_model = ActModuleExModel(context=self)
        info_dict = act_module_model.get_dict("ip_id=%s and is_release=1", params=[ip_id])
        if info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "popup_error"
            invoke_result_data.error_message = "当前主题下绑定的机台为发布状态，无法删除，需先下架该主题下所属的机台才可操作"
            return invoke_result_data

        return invoke_result_data

    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJingCan
        """
        ip_id = self.get_param_int("ip_id")
        act_id = self.get_param_int("act_id", 0)

        # 删除ip后把机台对应的ip都清空
        module_info_ex_model = ActModuleExModel(context=self)
        module_info_ex_model.update_table("ip_id=0", "ip_id=%s", ip_id)
        # 删除机台缓存

        business_base_model = BusinessBaseModel(context=self)
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module_list(act_id))

        return result_data