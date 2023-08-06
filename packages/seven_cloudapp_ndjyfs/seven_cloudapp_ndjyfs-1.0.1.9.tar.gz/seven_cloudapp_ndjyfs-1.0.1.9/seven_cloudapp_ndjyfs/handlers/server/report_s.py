# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-06-05 17:27:26
:LastEditTime: 2022-01-18 11:45:14
:LastEditors: HuangJingCan
:description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *

from seven_cloudapp_frame.models.db_models.stat.stat_report_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_orm_model import *

from seven_cloudapp_frame.handlers.server.report_s import StatReportListHandler
from seven_cloudapp_frame.handlers.server.report_s import TrendReportListHandler


class ReportTotalHandler(ClientBaseHandler):
    """
    :description: 各类总数统计
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 各类总数统计
        :param act_id：活动id
        :return dict
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")

        stat_report_model = StatReportModel(context=self)
        stat_orm_model = StatOrmModel(context=self)
        data_list = []

        # 获取顶部ORM统计块
        total_orm_list = stat_orm_model.get_dict_list("group_name='活动数据'")
        for orm in total_orm_list:
            #"TotalVisitManCount", "TotalLotteryUserCount", "TotalPayCount", "TotalRawardPrizeCount"
            #"总访问人数"         , "总抽奖人数"            , "总消费金额"    , "赏品发放数量"
            data = {}
            stat_report = stat_report_model.get_dict("act_id=%s and key_name=%s", field="sum(key_value) as key_value", params=[act_id, orm["key_name"]])
            data["value"] = stat_report["key_value"] if stat_report and stat_report["key_value"] else 0
            data["title"] = orm["key_value"]
            data_list.append(data)

        return self.response_json_success(data_list)


class StatReportListHandler(StatReportListHandler):
    def business_process_executed(self, stat_report_list, request_params):
        """
        :description: 执行后事件 -- 计算销售数据客单价
        :param stat_report_list:报表数据列表(表格)
        :return:
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        # self.logging_link_info("报表数据列表(表格):" + str(stat_report_list))  # todo 待注释
        result_list = []
        for group_data in stat_report_list:
            if "group_name" in group_data:
                if int(module_id) > 0 and group_data["group_name"] != "销售情况" and group_data["group_name"] != "参与情况":
                    #系列数据，过滤除销售情况的统计
                    continue
                if group_data["group_name"] == "参与情况" or group_data["group_name"] == "销售情况":
                    module_id = request_params["module_id"] if "module_id" in request_params.keys() else 0
                    if int(module_id) > 0:
                        data_list = []
                        key_name_module_str = "_" + str(module_id)
                        for data in group_data["data_list"]:
                            if key_name_module_str in data["name"]:
                                data_list.append(data)
                        group_data["data_list"] = data_list

            result_list.append(group_data)

            # if group_data["group_name"] == "营销效果":

            #             data = {}
            #             data[""]
            #             group_data["data_list"].append(data)
        for group_data in stat_report_list:
            if "group_name" in group_data:
                if group_data["group_name"] == "销售情况":
                    pay_user_count = 0
                    pay_money_count = 0
                    average_pay = 0
                    for data in group_data["data_list"]:
                        if data["title"] == "支付人数":
                            pay_user_count = data["value"]
                        elif data["title"] == "支付金额":
                            pay_money_count = data["value"]
                    # self.logging_link_info("客单价:" + str(pay_money_count) + str(type(pay_money_count)) + str(pay_user_count) + str(type(pay_user_count)))
                    average_pay = float(pay_money_count / pay_user_count) if pay_user_count > 0 else 0
                    group_data["data_list"].append({"title": "客单价", "value": average_pay})
        return result_list


class TrendReportListHandler(TrendReportListHandler):
    """
    :description: 报表数据列表(趋势图) 
    """
    def business_process_executed(self, trend_report_list, request_params):
        """
        :description: 执行后事件
        :param trend_report_list:报表数据列表(趋势图)
        :param request_params: 请求参数字典
        :return:
        :last_editors: HuangJingCan
        """
        result_list = []
        module_id = self.get_param_int("module_id")
        if int(module_id) > 0:
            for group_data in trend_report_list:
                if "group_name" in group_data:
                    if group_data["group_name"] != "销售情况" and group_data["group_name"] != "参与情况":
                        #系列数据，过滤除销售情况的统计
                        continue
                    data_list = []
                    for data in group_data["data_list"]:
                        if "_" in data["name"]:
                            data_list.append(data)
                    group_data["data_list"] = data_list
                    result_list.append(group_data)
        else:
            result_list = trend_report_list
        for group_data in result_list:
            if "group_name" in group_data:
                if group_data["group_name"] == "销售情况":
                    #支付人数数组
                    pay_user_count_list = []
                    #支付金额数组
                    pay_money_count_list = []
                    #客单价数组
                    customer_unit_price_list = []
                    for data in group_data["data_list"]:
                        if data["title"] == "支付人数":
                            pay_user_count_list = data["value"]
                        elif data["title"] == "支付金额":
                            pay_money_count_list = data["value"]

                    for pay_user_count in pay_user_count_list:
                        pay_money_count = [pay_money_count for pay_money_count in pay_money_count_list if pay_money_count["date"] == pay_user_count["date"]]
                        if pay_money_count:
                            average_pay = float(pay_money_count[0]["value"] / pay_user_count["value"]) if pay_user_count["value"] > 0 else 0
                        else:
                            average_pay = 0
                        customer_unit_price_list.append({"title": "客单价", "date": pay_user_count["date"], "value": average_pay})
                    customer_unit_price_data = {}
                    customer_unit_price_data["title"] = "客单价"
                    customer_unit_price_data["value"] = customer_unit_price_list
                    group_data["data_list"].append(customer_unit_price_data)

        return result_list