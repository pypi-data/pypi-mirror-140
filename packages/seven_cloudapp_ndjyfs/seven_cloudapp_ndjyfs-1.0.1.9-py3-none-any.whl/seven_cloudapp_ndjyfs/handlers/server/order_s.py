# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-06-02 11:08:39
:LastEditTime: 2022-02-17 11:31:08
:LastEditors: HuangJingCan
:description: 订单相关
"""
# from re import T
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.libs.customize.oss2_helper import *
from seven_cloudapp_frame.libs.customize.seven_helper import *

from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_pay_order_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_order_model import *
from seven_cloudapp_frame.models.db_models.ip.ip_info_model import *

from seven_cloudapp_frame.handlers.server.order_s import PayOrderListHandler
from seven_cloudapp_frame.handlers.server.order_s import TaoPayOrderExportHandler
from seven_cloudapp_frame.handlers.server.order_s import PrizeOrderListHandler
from seven_cloudapp_frame.handlers.server.order_s import PrizeOrderExportHandler
from seven_cloudapp_frame.handlers.server.order_s import ImportPrizeOrderHandler
from seven_cloudapp_frame.handlers.server.order_s import UpdatePrizeOrderStatusHandler
from seven_cloudapp_frame.handlers.server.order_s import UpdatePrizeOrderSellerRemarkHandler
from seven_cloudapp_frame.models.ip_base_model import IpBaseModel

from seven_cloudapp_ndjyfs.models.db_models.act.act_module_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.prize.prize_roster_ex_model import *
from seven_cloudapp_ndjyfs.models.business_base_model import *


class UpdatePrizeOrderStatusHandler(UpdatePrizeOrderStatusHandler):
    """
    :description: 更新订单状态
    """
    def business_process_executing(self):
        """
        :description: 执行前事件
        :param 
        :return: InvokeResultData
        :last_editors: HuangJingCan
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"prize_roster_sub_table": "ex"}
        return invoke_result_data


class PayOrderListHandler(PayOrderListHandler):
    """
    :description: 支付订单列表
    """
    def business_process_executing(self):
        """
        :description: 执行前事件
        :param 
        :return: InvokeResultData
        :last_editors: HuangJingCan
        """
        params = []
        condition = ConditionWhere()

        main_pay_order_no = self.get_param("main_pay_order_no")
        sub_pay_order_no = self.get_param("sub_pay_order_no")
        price_gear_name = self.get_param("price_gear_name")

        if main_pay_order_no != "":
            condition.add_condition("main_pay_order_no=%s")
            params.append(main_pay_order_no)
        if sub_pay_order_no != "":
            condition.add_condition("sub_pay_order_no=%s")
            params.append(sub_pay_order_no)
        if price_gear_name != "":
            condition.add_condition("s1=%s")
            params.append(price_gear_name)

        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"condition": condition.to_string(), "params": params}

        return invoke_result_data


class TaoPayOrderExportHandler(TaoPayOrderExportHandler):
    """
    :description: 支付订单导出
    """
    def business_process_executing(self):
        """
        :description: 执行前事件
        :param 
        :return: InvokeResultData
        :last_editors: HuangJingCan
        """
        params = []
        condition = ConditionWhere()

        price_gear_name = self.get_param("price_gear_name")

        if price_gear_name != "":
            condition.add_condition("s1=%s")
            params.append(price_gear_name)

        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"condition": condition.to_string(), "params": params}

        return invoke_result_data

    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data:result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJingCan
        """
        result_list = []
        for tao_pay_order_dict in result_data:
            data_row = {}
            data_row["淘宝主订单号"] = tao_pay_order_dict["main_pay_order_no"]
            data_row["淘宝子订单号"] = tao_pay_order_dict["sub_pay_order_no"]
            data_row["淘宝名"] = tao_pay_order_dict["user_nick"]
            data_row["商家编码"] = tao_pay_order_dict["goods_code"]
            data_row["商品名称"] = tao_pay_order_dict["goods_name"]
            data_row["档位名称"] = tao_pay_order_dict["s1"]
            data_row["购买数量"] = tao_pay_order_dict["buy_num"]
            data_row["支付金额"] = tao_pay_order_dict["pay_price"]
            data_row["支付时间"] = TimeHelper.datetime_to_format_time(tao_pay_order_dict["pay_date"])
            result_list.append(data_row)
        return result_list


class ImportPrizeOrderHandler(ImportPrizeOrderHandler):
    """
    :description: 导入奖品订单进行发货
    """
    def business_process_executing(self):
        """
        :description: 执行前事件
        :return:
        :last_editors: HuangJingCan
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"prize_roster_sub_table": "ex"}
        return invoke_result_data


class PrizeOrderExportHandler(PrizeOrderExportHandler):
    """
    :description: 发货订单批量导出
    """
    def business_process_executing(self):
        """
        :description: 执行前事件
        :return:
        :last_editors: HuangJingCan
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {"prize_roster_sub_table": "ex"}
        return invoke_result_data

    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data:result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJingCan
        """
        result_list = []
        if len(result_data) > 0:
            frame_base_model = FrameBaseModel(context=self)
            business_base_model = BusinessBaseModel(context=self)
            for prize_order in result_data:
                for prize_roster in prize_order["roster_list"]:
                    data_row = {}
                    data_row["小程序订单号"] = prize_order["order_no"]
                    data_row["淘宝主订单号"] = prize_roster["main_pay_order_no"]
                    data_row["淘宝子订单号"] = prize_roster["sub_pay_order_no"]
                    data_row["淘宝名"] = prize_order["user_nick"]
                    data_row["机台名称"] = prize_roster["module_name"]
                    data_row["奖品长名称"] = prize_roster["prize_title"]
                    data_row["奖品短名称"] = prize_roster["prize_name"]
                    data_row["番赏等级"] = prize_roster["yfs_grade"]
                    data_row["商家编码"] = prize_roster["goods_code"]
                    data_row["奖品价值"] = str(prize_roster["prize_price"])
                    data_row["奖品类型"] = business_base_model.get_prize_type_name(prize_roster["prize_type"])
                    data_row["姓名"] = prize_order["real_name"]
                    data_row["手机号"] = prize_order["telephone"]
                    data_row["省份"] = prize_order["province"]
                    data_row["城市"] = prize_order["city"]
                    data_row["区县"] = prize_order["county"]
                    data_row["街道"] = prize_order["street"]
                    data_row["收货地址"] = prize_order["address"]
                    data_row["物流单号"] = prize_order["express_no"]
                    data_row["物流公司"] = prize_order["express_company"]
                    data_row["发货时间"] = "" if str(prize_order["deliver_date"]) == "1900-01-01 00:00:00" else str(prize_order["deliver_date"])
                    data_row["订单状态"] = frame_base_model.get_order_status_name(prize_order["order_status"])
                    data_row["备注"] = prize_order["seller_remark"]
                    result_list.append(data_row)
        return result_list


class PrizeRosterListHandler(ClientBaseHandler):
    """
    :description: 用户奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户奖品列表
        :param act_id ：act_id
        :param module_id: 机台id （从机台列表跳转使用）
        :param goods_code: 商家编码 （从机台列表跳转使用）
        :param tb_user_id：用户id （从用户列表跳转使用）
        :param prize_order_id：发货订单id（从发货列表跳转使用）
        :param nick_name：淘宝名称（查询条件）
        :param prize_name：奖品名称（查询条件）    
        :param module_name：机台名称（查询条件）
        :param ip_id: 主题id（查询条件）
        :param module_type：抽赏模式:1次数2积分3一番赏4叠叠赏
        :param prize_type：奖品类型（查询条件）0全部1现货2优惠券3红包4参与奖5预售   
        :param prize_status：奖品状态（查询条件）-1全部 （不包括已删除）0未下单，1已下单，2已回购，10已删除\隐藏（状态3千牛端不予选择）
        :param create_date_start：开始时间（查询条件）
        :param create_date_end：结束时间（查询条件）
        :return: 
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)
        # 跳转索引
        module_id = self.get_param_int("module_id")
        user_id = self.get_param_int("tb_user_id")
        prize_order_id = self.get_param_int("prize_order_id")
        goods_code = self.get_param("goods_code")
        # 查询条件
        user_nick = self.get_param("nick_name")
        prize_name = self.get_param("prize_name")
        module_name = self.get_param("module_name")
        ip_id = self.get_param_int("ip_id")
        module_type = self.get_param_int("module_type")
        prize_type = self.get_param_int("prize_type")  #  0 全部1现货5预售
        prize_status = self.get_param_int("prize_status", -1)
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")

        ip_info_model = IpInfoModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s AND prize_status!=10")

        if module_id > 0:
            condition.add_condition("module_id=%s")
            params.append(module_id)
        if goods_code != "":
            condition.add_condition("goods_code=%s")
            params.append(goods_code)
        if user_id > 0:
            condition.add_condition("user_id=%s")
            params.append(user_id)
        if prize_order_id > 0:
            condition.add_condition("prize_order_id=%s")
            params.append(prize_order_id)
        if user_nick != "":
            condition.add_condition("user_nick=%s")
            params.append(user_nick)
        if prize_name:
            condition.add_condition("prize_name=%s")
            params.append(prize_name)
        if module_name != "":
            condition.add_condition("module_name like %s")
            module_name = f"%{module_name}%"
            params.append(module_name)
        if ip_id > 0:
            condition.add_condition("ip_id=%s")
            params.append(ip_id)
        if module_type > 0:
            condition.add_condition("module_type=%s")
            params.append(module_type)
        if prize_type > 0:
            condition.add_condition("prize_type=%s")
            params.append(prize_type)
        # 已删除的不再在千牛端展示和用户背包展示
        if prize_status > -1:
            condition.add_condition("prize_status=%s")
            params.append(prize_status)
        if create_date_start:
            condition.add_condition("create_date>=%s")
            params.append(create_date_start)
        if create_date_end:
            condition.add_condition("create_date<=%s")
            params.append(create_date_end)

        prize_roster_list, total = prize_roster_ex_model.get_dict_page_list("*", page_index, page_size, condition.to_string(), order_by="create_date desc", params=params)

        if prize_roster_list:
            ip_dict_list = ip_info_model.get_dict_list("act_id=%s", field="id,ip_name", params=[act_id])
            prize_roster_list = SevenHelper.merge_dict_list(prize_roster_list, "ip_id", ip_dict_list, "id", "ip_name")
            for prize_roster in prize_roster_list:
                prize_roster["module_type_name"] = business_base_model.get_module_type_name(prize_roster["module_type"])
                prize_roster["module_price_name"] = str(prize_roster["module_price"]) + business_base_model.get_module_type_unit(prize_roster["module_type"])
                prize_roster["prize_type_name"] = business_base_model.get_prize_type_name(prize_roster["prize_type"])
                prize_roster["prize_status_name"] = business_base_model.get_prize_status_name(prize_roster["prize_status"])

        page_info = PageInfo(page_index, page_size, total, prize_roster_list)

        return self.response_json_success(page_info)


class PrizeRosterListExportHandler(ClientBaseHandler):
    """
    :description: 批量奖品列表导出
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 批量奖品列表导出
        :param act_id ：act_id
        :param module_id: 机台id （从机台列表跳转使用）
        :param goods_code: 商家编码 （从机台列表跳转使用）
        :param tb_user_id：用户id （从用户列表跳转使用）
        :param prize_order_id：发货订单id（从发货列表跳转使用）
        :param nick_name：淘宝名称（查询条件）
        :param prize_name：奖品名称（查询条件）    
        :param module_name：机台名称（查询条件）
        :param ip_id: 主题id（查询条件）
        :param module_type：抽赏模式:1次数2积分3一番赏4叠叠赏
        :param prize_type：奖品类型（查询条件）0全部1现货2优惠券3红包4参与奖5预售   
        :param prize_status：奖品状态（查询条件）-1全部 （不包括已删除）0未下单，1已下单，2已回购，10已删除\隐藏（状态3千牛端不予选择）
        :param create_date_start：开始时间（查询条件）
        :param create_date_end：结束时间（查询条件）
        :return: 
        :last_editors: HuangJingCan
        """
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 500)
        act_id = self.get_param_int("act_id")
        # 跳转索引
        module_id = self.get_param_int("module_id")
        user_id = self.get_param_int("tb_user_id")
        prize_order_id = self.get_param_int("prize_order_id")
        goods_code = self.get_param("goods_code")
        # 查询条件
        user_nick = self.get_param("nick_name")
        prize_name = self.get_param("prize_name")
        module_name = self.get_param("module_name")
        ip_id = self.get_param_int("ip_id")
        module_type = self.get_param_int("module_type")
        prize_type = self.get_param_int("prize_type")  #  0 全部1现货5预售
        prize_status = self.get_param_int("prize_status", -1)
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s and prize_status!=10")

        if module_id > 0:
            condition.add_condition("module_id=%s")
            params.append(module_id)
        if goods_code != "":
            condition.add_condition("goods_code=%s")
            params.append(goods_code)
        if user_id > 0:
            condition.add_condition("user_id=%s")
            params.append(user_id)
        if prize_order_id > 0:
            condition.add_condition("prize_order_id=%s")
            params.append(prize_order_id)
        if user_nick != "":
            condition.add_condition("user_nick=%s")
            params.append(user_nick)
        if prize_name:
            condition.add_condition("prize_name=%s")
            params.append(prize_name)
        if module_name != "":
            condition.add_condition("module_name like %s")
            module_name = f"%{module_name}%"
            params.append(module_name)
        if ip_id > 0:
            condition.add_condition("ip_id=%s")
            params.append(ip_id)
        if module_type > 0:
            condition.add_condition("module_type=%s")
            params.append(module_type)
        if prize_type > 0:
            condition.add_condition("prize_type=%s")
            params.append(prize_type)
        # 已删除的不再在千牛端展示和用户背包展示
        if prize_status > -1:
            condition.add_condition("prize_status=%s")
            params.append(prize_status)
        if create_date_start:
            condition.add_condition("create_date>=%s")
            params.append(create_date_start)
        if create_date_end:
            condition.add_condition("create_date<=%s")
            params.append(create_date_end)

        ip_info_model = IpInfoModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        # 取数据并导出
        max_size = 100
        multiple = page_size // max_size  # 页大小倍数
        begin_page_index = page_index * multiple  # 开始页码

        # 生成数据，导出execl
        result_data = []  # 结果集
        is_break = False
        for i in range(multiple):
            if is_break:
                break

            #奖品订单
            prize_roster_list, total = prize_roster_ex_model.get_dict_page_list("*", begin_page_index + i, max_size, condition.to_string(), order_by="create_date desc", params=params)
            if prize_roster_list:
                ip_dict_list = ip_info_model.get_dict_list("act_id=%s", field="id,ip_name", params=[act_id])
                prize_roster_list = SevenHelper.merge_dict_list(prize_roster_list, "ip_id", ip_dict_list, "id", "ip_name")
                #订单奖品
                for prize_roster in prize_roster_list:
                    data_row = {}
                    data_row["小程序订单号"] = prize_roster["order_no"]
                    # data_row["淘宝主订单号"] = prize_roster["main_pay_order_no"]
                    data_row["淘宝子订单号"] = prize_roster["sub_pay_order_no"]
                    data_row["淘宝名"] = prize_roster["user_nick"]
                    data_row["主题名称"] = prize_roster["ip_name"]
                    data_row["机台名称"] = prize_roster["module_name"]
                    data_row["扭蛋模式"] = business_base_model.get_module_type_name(prize_roster["module_type"])
                    data_row["扭蛋价格"] = str(prize_roster["module_price"]) + business_base_model.get_module_type_unit(prize_roster["module_type"])
                    data_row["奖品名称"] = prize_roster["prize_name"]
                    data_row["奖品价值"] = str(prize_roster["prize_price"])
                    data_row["番赏等级"] = prize_roster["yfs_grade"]
                    data_row["回购积分"] = prize_roster["buy_back_integral"]
                    data_row["商家编码"] = prize_roster["goods_code"]
                    data_row["奖品类型"] = business_base_model.get_prize_type_name(prize_roster["prize_type"])
                    data_row["获得时间"] = TimeHelper.datetime_to_format_time(prize_roster["create_date"])
                    data_row["状态"] = business_base_model.get_prize_status_name(prize_roster["prize_status"])
                    result_data.append(data_row)
            else:
                is_break = True

        resource_path = ""
        #导入Excel
        if result_data:
            resource_path = OSS2Helper().export_excel(result_data)

        return self.response_json_success(resource_path)


class HidePrizeRosterHandler(ClientBaseHandler):
    """
    :description: 隐藏用户奖品
    """
    @filter_check_params("prize_roster_id")
    def get_async(self):
        """
        :description: 用户奖品列表
        :param prize_roster_id:用户奖品id
        :return: 
        :last_editors: HuangJingCan
        """
        prize_roster_id = self.get_param_int("prize_roster_id")

        prize_roster_ex_model = PrizeRosterExModel(context=self)

        if prize_roster_id:
            modify_date = self.get_now_datetime()
            prize_roster = prize_roster_ex_model.get_entity_by_id(prize_roster_id)
            if prize_roster and prize_roster.is_del == 0 and prize_roster.prize_status == 0:
                # 只有未下单奖品可以隐藏
                prize_roster_ex_model.update_table("prize_status=10,modify_date=%s", "id=%s and prize_status=0", [modify_date, prize_roster_id])
                return self.response_json_success()
            self.logging_link_info("【奖品信息】：" + str(prize_roster))

        return self.response_json_error("ErrorId", "删除奖品异常")


class BuyBackListHandler(ClientBaseHandler):
    """
    :description: 回购奖品表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description:回购奖品表
        :param act_id ：act_id
        :param tb_user_id：用户id （从用户列表跳转使用）
        :param nick_name：淘宝名称（查询条件）      
        :param prize_name：奖品名称（查询条件）    
        :param goods_code：商家编码（查询条件）
        :param buy_back_start：开始时间（查询条件）
        :param buy_back_end：结束时间（查询条件）
        :return: 
        :last_editors: HuangJingCan
        """
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)
        act_id = self.get_param_int("act_id")
        # 跳转索引
        user_id = self.get_param_int("tb_user_id")
        # 查询条件
        user_nick = self.get_param("nick_name")
        prize_name = self.get_param("prize_name")
        goods_code = self.get_param("goods_code")
        buy_back_start = self.get_param("buy_back_start")
        buy_back_end = self.get_param("buy_back_end")

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s AND prize_status=2")

        if user_id:
            condition.add_condition("user_id=%s")
            params.append(user_id)
        if user_nick != "":
            condition.add_condition("user_nick=%s")
            params.append(user_nick)
        if prize_name:
            condition.add_condition("prize_name=%s")
            params.append(prize_name)
        if goods_code:
            condition.add_condition("goods_code=%s")
            params.append(goods_code)
        if buy_back_start:
            condition.add_condition("buy_back_date>=%s")
            params.append(buy_back_start)
        if buy_back_end:
            condition.add_condition("buy_back_date<=%s")
            params.append(buy_back_end)

        ip_info_model = IpInfoModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)
        #奖品订单
        page_list, total = prize_roster_ex_model.get_dict_page_list("*", page_index, page_size, condition.to_string(), order_by="buy_back_date desc", params=params)

        ip_dict_list = ip_info_model.get_dict_list("act_id=%s", field="id,ip_name", params=[act_id])
        page_list = SevenHelper.merge_dict_list(page_list, "ip_id", ip_dict_list, "id", "ip_name")

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.response_json_success(page_info)


class BuyBackListExportHandler(ClientBaseHandler):
    """
    :description: 回购奖品列表导出
    """
    def get_async(self):
        """
        :description: 回购奖品列表导出
        :param act_id ：act_id
        :param tb_user_id：用户id （从用户列表跳转使用）
        :param nick_name：淘宝名称（查询条件）      
        :param prize_name：奖品名称（查询条件）    
        :param goods_code：商家编码（查询条件）
        :param buy_back_start：开始时间（查询条件）
        :param buy_back_end：结束时间（查询条件）
        :return: 
        :last_editors: HuangJingCan
        """
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)
        act_id = self.get_param_int("act_id")
        # 跳转索引
        user_id = self.get_param_int("tb_user_id")
        # 查询条件
        user_nick = self.get_param("nick_name")
        prize_name = self.get_param("prize_name")
        goods_code = self.get_param("goods_code")
        buy_back_start = self.get_param("buy_back_start")
        buy_back_end = self.get_param("buy_back_end")

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s AND prize_status=2")

        if user_id:
            condition.add_condition("user_id=%s")
            params.append(user_id)
        if user_nick != "":
            condition.add_condition("user_nick=%s")
            params.append(user_nick)
        if prize_name:
            condition.add_condition("prize_name=%s")
            params.append(prize_name)
        if goods_code:
            condition.add_condition("goods_code=%s")
            params.append(goods_code)
        if buy_back_start:
            condition.add_condition("buy_back_date>=%s")
            params.append(buy_back_start)
        if buy_back_end:
            condition.add_condition("buy_back_date<=%s")
            params.append(buy_back_end)

        ip_info_model = IpInfoModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)

        # 取数据并导出
        max_size = 100
        multiple = page_size // max_size  # 页大小倍数
        begin_page_index = page_index * multiple  # 开始页码

        # 生成数据，导出execl
        result_data = []  # 结果集
        is_break = False
        for i in range(multiple):
            if is_break:
                break
            prize_roster_list, total = prize_roster_ex_model.get_dict_page_list("*", begin_page_index + i, max_size, condition.to_string(), order_by="buy_back_date desc", params=params)
            if prize_roster_list:
                ip_dict_list = ip_info_model.get_dict_list("act_id=%s", field="id,ip_name", params=[act_id])
                prize_roster_list = SevenHelper.merge_dict_list(prize_roster_list, "ip_id", ip_dict_list, "id", "ip_name")
                #订单奖品
                for prize_roster in prize_roster_list:
                    data_row = {}
                    data_row["淘宝名"] = prize_roster["user_nick"]
                    data_row["主题名称"] = prize_roster["ip_name"]
                    data_row["机台名称"] = prize_roster["module_name"]
                    data_row["奖品名称"] = prize_roster["prize_name"]
                    data_row["奖品图片"] = prize_roster["prize_pic"]
                    data_row["番赏等级"] = prize_roster["yfs_grade"]
                    data_row["商家编码"] = prize_roster["goods_code"]
                    data_row["回购积分"] = prize_roster["buy_back_integral"]
                    data_row["回购时间"] = TimeHelper.datetime_to_format_time(prize_roster["buy_back_date"])
                    result_data.append(data_row)
            else:
                is_break = True
        resource_path = ""
        #导入Excel
        if result_data:
            resource_path = OSS2Helper().export_excel(result_data)

        return self.response_json_success(resource_path)


class PresalePrizeListHandler(ClientBaseHandler):
    """
    :description: 预售奖品表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 预售奖品表
        :param act_id ：act_id
        :param tb_user_id：用户id （从用户列表跳转使用）
        :param nick_name：淘宝名称（查询条件）      
        :param goods_code：商家编码（查询条件）    
        :param sale_status：发售状态-1全部0未发售1已发售（查询条件）
        :param ip_id: 主题id（查询条件）
        :param create_date_start：开始时间（查询条件）
        :param create_date_end：结束时间（查询条件）
        :return: 
        :last_editors: HuangJingCan
        """
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)
        act_id = self.get_param_int("act_id")
        # 跳转索引
        user_id = self.get_param_int("tb_user_id")
        # 查询条件
        user_nick = self.get_param("nick_name")
        goods_code = self.get_param("goods_code")
        ip_id = self.get_param_int("ip_id")
        sale_status = self.get_param_int("sale_status", -1)
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s AND prize_status!=10 AND prize_type=5")

        if user_id > 0:
            condition.add_condition("user_id=%s")
            params.append(user_id)
        if user_nick != "":
            condition.add_condition("user_nick=%s")
            params.append(user_nick)
        if goods_code:
            condition.add_condition("goods_code=%s")
            params.append(goods_code)
        if ip_id > 0:
            condition.add_condition("ip_id=%s")
            params.append(ip_id)
        if sale_status > -1:
            condition.add_condition("sale_status=%s")
            params.append(sale_status)
        if create_date_start:
            condition.add_condition("create_date>=%s")
            params.append(create_date_start)
        if create_date_end:
            condition.add_condition("create_date<=%s")
            params.append(create_date_end)

        # 奖品订单
        ip_info_model = IpInfoModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)

        page_list, total = prize_roster_ex_model.get_dict_page_list("*", page_index, page_size, condition.to_string(), order_by="create_date desc", params=params)

        ip_dict_list = ip_info_model.get_dict_list("act_id=%s", field="id,ip_name", params=[act_id])
        page_list = SevenHelper.merge_dict_list(page_list, "ip_id", ip_dict_list, "id", "ip_name")

        page_info = PageInfo(page_index, page_size, total, page_list)

        self.response_json_success(page_info)


class PresalePrizeListExportHandler(ClientBaseHandler):
    """
    :description: 导出预售奖品表
    """
    def get_async(self):
        """
        :description: 导出预售奖品表
        :param act_id ：act_id
        :param tb_user_id：用户id （从用户列表跳转使用）
        :param nick_name：淘宝名称（查询条件）      
        :param goods_code：商家编码（查询条件）    
        :param sale_status：发售状态-1全部0未发售1已发售（查询条件）
        :param ip_id: 主题id（查询条件）
        :param create_date_start：开始时间（查询条件）
        :param create_date_end：结束时间（查询条件）
        :return: 
        :last_editors: HuangJingCan
        """
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 500)
        act_id = self.get_param_int("act_id")
        # 跳转索引
        user_id = self.get_param_int("tb_user_id")
        # 查询条件
        user_nick = self.get_param("nick_name")
        goods_code = self.get_param("goods_code")
        ip_id = self.get_param_int("ip_id")
        sale_status = self.get_param_int("sale_status", -1)
        create_date_start = self.get_param("create_date_start")
        create_date_end = self.get_param("create_date_end")

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s AND prize_status!=10 AND prize_type=5")

        if user_id > 0:
            condition.add_condition("user_id=%s")
            params.append(user_id)
        if user_nick != "":
            condition.add_condition("user_nick=%s")
            params.append(user_nick)
        if goods_code:
            condition.add_condition("goods_code=%s")
            params.append(goods_code)
        if ip_id > 0:
            condition.add_condition("ip_id=%s")
            params.append(ip_id)
        if sale_status > -1:
            condition.add_condition("sale_status=%s")
            params.append(sale_status)
        if create_date_start:
            condition.add_condition("create_date>=%s")
            params.append(create_date_start)
        if create_date_end:
            condition.add_condition("create_date<=%s")
            params.append(create_date_end)

        # 奖品订单
        ip_info_model = IpInfoModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)
        business_base_model = BusinessBaseModel(context=self)
        # 取数据并导出
        max_size = 100
        multiple = page_size // max_size  # 页大小倍数
        begin_page_index = page_index * multiple  # 开始页码

        # 生成数据，导出execl
        result_data = []  # 结果集
        is_break = False
        for i in range(multiple):
            if is_break:
                break
            prize_roster_list, total = prize_roster_ex_model.get_dict_page_list("*", begin_page_index + i, max_size, condition.to_string(), order_by="create_date desc", params=params)
            if prize_roster_list:
                ip_dict_list = ip_info_model.get_dict_list("act_id=%s", field="id,ip_name", params=[act_id])
                prize_roster_list = SevenHelper.merge_dict_list(prize_roster_list, "ip_id", ip_dict_list, "id", "ip_name")
                #订单奖品
                for prize_roster in prize_roster_list:
                    data_row = {}
                    # data_row["淘宝子订单号"] = prize_roster["sub_pay_order_no"]
                    data_row["淘宝名"] = prize_roster["user_nick"]
                    data_row["主题名称"] = prize_roster["ip_id"]
                    data_row["机台名称"] = prize_roster["module_name"]
                    data_row["奖品名称"] = prize_roster["prize_name"]
                    data_row["奖品价值"] = str(prize_roster["prize_price"])
                    data_row["商家编码"] = prize_roster["goods_code"]
                    data_row["状态"] = business_base_model.get_sale_status_name(prize_roster["sale_status"])
                    data_row["获得时间"] = TimeHelper.datetime_to_format_time(prize_roster["create_date"])
                    result_data.append(data_row)
            else:
                is_break = True
        resource_path = ""
        #导入Excel
        if result_data:
            resource_path = OSS2Helper().export_excel(result_data)

        return self.response_json_success(resource_path)


class PresalePrizeConfigListHandler(ClientBaseHandler):
    """
    :description: 预售奖品配置表
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description: 预售奖品表
        :param module_id: module_id
        :return: 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)  # 上限暂时设置100，如果不过再增加

        condition = "module_id=%s AND prize_type=5 AND is_del=0"
        params = [module_id]

        # 预售奖品表
        act_prize_ex_model = ActPrizeExModel(context=self)

        page_list, total = act_prize_ex_model.get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)
        # self.logging_link_info("【奖品】" + str(page_list) + "【奖品数量】：" + str(total))
        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.response_json_success(page_info)


class DeliverSalePrizeHandler(ClientBaseHandler):
    """
    :description:  发售预售奖品
    """
    @filter_check_params("module_id,prize_ids")
    def get_async(self):
        """
        :description: 发售预售奖品
        :param module_id: module_id
        :param prize_ids: 奖品id列表
        :return: 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        prize_ids = self.get_param("prize_ids")
        now_date = self.get_now_datetime()

        act_prize_ex_model = ActPrizeExModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)
        module_info_ex_model = ActModuleExModel(context=self)

        # prize_ids = str(prize_ids)[1:-1]

        condition = SevenHelper.get_condition_by_int_list("id", prize_ids)
        if condition == "":
            return self.response_json_error_params()

        act_prize_ex_model.update_table("sale_status=1", condition)
        # prize_roster_ex_model.update_table("sale_status=1", "prize_id in (%s)", prize_ids)

        # 预售奖品更新倒计时
        module_info_ex = module_info_ex_model.get_dict_by_id(module_id)
        automatic_buy_back_end_date = TimeHelper.add_days_by_format_time(now_date, module_info_ex["automatic_buy_back_days"])  # 自动回购结束时间戳
        # where += " and is_automatic_buy_back=1"
        condition = SevenHelper.get_condition_by_int_list("prize_id", prize_ids)
        prize_roster_ex_model.update_table("sale_status=1,automatic_buy_back_end_date=%s", condition, params=[automatic_buy_back_end_date])

        return self.response_json_success()