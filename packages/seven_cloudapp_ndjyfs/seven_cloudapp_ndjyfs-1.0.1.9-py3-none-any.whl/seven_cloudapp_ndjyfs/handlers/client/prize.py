# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-03-19 10:23:13
@LastEditTime: 2022-02-22 16:33:30
@LastEditors: ChenCheng
:Description: 奖品
"""
from dataclasses import dataclass
from multiprocessing import Condition
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.libs.customize.seven_helper import *

from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.asset_base_model import AssetBaseModel
from seven_cloudapp_frame.models.user_base_model import UserBaseModel

from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_pay_order_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_order_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *

from seven_cloudapp_ndjyfs.models.db_models.act.act_info_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_module_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.prize.prize_roster_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.user.user_info_ex_model import *
from seven_cloudapp_ndjyfs.models.business_base_model import *


class YfsPrizeTotalHandler(ClientBaseHandler):
    """
    :description: 获取一番赏奖品统计
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description:  获取一番赏奖品统计
        :param module_id: 机台id
        :return: 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")

        act_prize_ex_model = ActPrizeExModel(context=self)

        field = "yfs_grade,yfs_key_name,CAST(SUM(prize_total) AS SIGNED) AS prize_total,CAST(SUM(surplus) AS SIGNED) AS surplus"
        condition = "module_id=%s and is_del=0 and is_release=1"

        data = {}
        data["special_yfs"] = 0
        is_first = False
        first_surplus = 0
        is_last = False
        last_surplus = 0
        act_prize_list = act_prize_ex_model.get_dict_list(condition, order_by="sort_index desc", group_by="yfs_grade", field=field, params=module_id)
        for act_prize in act_prize_list:
            act_prize["hand_out"] = act_prize["prize_total"] - act_prize["surplus"]
            if act_prize["yfs_key_name"] == "First":
                is_first = True
                first_surplus = act_prize["surplus"]
            if act_prize["yfs_key_name"] == "Last":
                is_last = True
                last_surplus = act_prize["surplus"]

        data["prize_list"] = act_prize_list

        if is_first == True and first_surplus > 0:
            data["special_yfs"] = 1
        if is_last == True and first_surplus <= 0:
            data["special_yfs"] = 2
        if first_surplus <= 0 and last_surplus <= 0:
            data["special_yfs"] = 3

        return self.response_json_success(data)


class PrizeListHandler(ClientBaseHandler):
    """
    :description: 获取机台奖品列表
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description:  获取机台奖品列表
        :param act_id: 活动id
        :param module_id: 机台id
        :param page_index: 页索引
        :param page_size: 页大小
        :return: 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 20)

        act_prize_ex_model = ActPrizeExModel(context=self)

        field = "id,prize_name,prize_title,prize_pic,prize_type,tag_id,prize_detail_json,prize_price,yfs_type,yfs_grade,yfs_key_name,sale_status,surplus,prize_total,probability,first_open_threshold,last_open_threshold,dd_open_step,dd_open_threshold"
        act_prize_list, total = act_prize_ex_model.get_dict_page_list(field, page_index, page_size, "module_id=%s and is_del=0 and is_release=1", "", "sort_index desc", module_id)

        prize_sum_probability = 0  # 奖品总权重

        prize_sum_dict = act_prize_ex_model.get_dict("module_id=%s and is_del=0 and is_release=1 and yfs_type=1", field="CAST(SUM(probability) AS SIGNED) AS prize_sum_probability", params=module_id)
        prize_sum_probability = prize_sum_dict["prize_sum_probability"] if prize_sum_dict["prize_sum_probability"] else 0

        # 叠叠赏列表
        special_dd_list = act_prize_ex_model.get_dict_list("module_id=%s and is_del=0 and is_release=1 and yfs_type=3", order_by="dd_open_step ASC", field=field, params=module_id)
        for act_prize in act_prize_list:
            act_prize["chance"] = round(act_prize["probability"] / prize_sum_probability * 100, 2) if prize_sum_probability else 0
            act_prize["hand_out"] = act_prize["prize_total"] - act_prize["surplus"]

        page_info = PageInfo(page_index, page_size, total, act_prize_list)
        page_info.special_dd_list = special_dd_list

        return self.response_json_success(page_info)


class PrizeTotalSurplusHandler(ClientBaseHandler):
    """
    :description: 获取奖品库存
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description:  获取奖品库存
        :param act_id: 活动id
        :param module_id: 机台id
        :return: 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")

        prize_total_sum = 0  # 奖品库存总数量
        prize_surplus_sum = 0  # 奖品库存剩余总数量

        act_prize_ex_model = ActPrizeExModel(context=self)

        field = "CAST(SUM(prize_total) AS SIGNED) AS prize_total_sum, CAST(SUM(surplus) AS SIGNED) AS prize_surplus_sum"

        prize_sum_dict = act_prize_ex_model.get_dict("module_id=%s and is_del=0 and is_release=1 and yfs_type=1", field=field, params=module_id)
        prize_total_sum = prize_sum_dict["prize_total_sum"] if prize_sum_dict["prize_total_sum"] else 0
        prize_surplus_sum = prize_sum_dict["prize_surplus_sum"] if prize_sum_dict["prize_surplus_sum"] else 0

        prize_info = {}
        prize_info["prize_total"] = prize_total_sum
        prize_info["prize_surplus"] = prize_surplus_sum
        prize_info["hand_out"] = prize_total_sum - prize_surplus_sum

        return self.response_json_success(prize_info)


class PrizeRosterListHandler(ClientBaseHandler):
    """
    :description: 中奖记录列表
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description: 中奖记录列表
        :param module_id: 机台id
        :param page_index: 页索引
        :param page_size: 页大小
        :return 列表
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 20)

        prize_roster_ex_model = PrizeRosterExModel(context=self)

        params = [module_id]
        condition = ConditionWhere()
        condition.add_condition("module_id=%s and is_del=0")

        # 获取中奖记录
        prize_roster_list, total = prize_roster_ex_model.get_dict_page_list("*", page_index, page_size, condition.to_string(), "", "id desc", params)

        page_info = PageInfo(page_index, page_size, total, prize_roster_list)

        return self.response_json_success(page_info)


class BackpackRedHandler(ClientBaseHandler):
    """
    :description: 获取用户背包红点接口（判断是否存在未下单奖品）
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        act_id = self.get_param_int("act_id")
        user_id = self.get_param_int("tb_user_id")
        prize_roster_ex_model = PrizeRosterExModel(context=self)
        condition = ConditionWhere()
        condition.add_condition("user_id=%s and act_id=%s and is_del=0 and prize_status=0")
        params = [user_id, act_id]
        prize_roster = prize_roster_ex_model.get_cache_dict(condition.to_string(),params=params)
        if prize_roster:
            return self.response_json_success(1)
        else:
            return self.response_json_success(0)


class UserPrizeListHandler(ClientBaseHandler):
    """
    :description: 获取用户奖品列表(背包)
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 获取用户奖品列表
        :param act_id：活动id
        :param tb_user_id：用户id
        :param ip_id: IP id
        :param page_index：页索引
        :param page_size：页大小
        :param prize_type：奖品类型：0全部1现货5预售
        :param sale_status: 发售状态：-1全部，0未发售，1已发售
        :param is_open_buy_back: 是否可回购
        :return: 
        :last_editors: HuangJingCan
        """
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)
        act_id = self.get_param_int("act_id")
        user_id = self.get_param_int("tb_user_id")
        ip_id = self.get_param_int("ip_id")
        prize_type = self.get_param_int("prize_type", 1)
        sale_status = self.get_param_int("sale_status", -1)
        is_open_buy_back = self.get_param_int("is_open_buy_back", -1)

        prize_roster_ex_model = PrizeRosterExModel(context=self)
        # prize_order_model = PrizeOrderModel(context=self)

        condition = ConditionWhere()
        condition.add_condition("user_id=%s and act_id=%s and is_del=0 and prize_status=0")
        params = [user_id, act_id]
        order_by = "id desc"
        field = "id,prize_id,prize_name,prize_title,prize_pic,prize_status,tag_id,yfs_grade,yfs_key_name,sale_status,is_open_buy_back,buy_back_integral,automatic_buy_back_days,automatic_buy_back_end_date,create_date,prize_type,yfs_type"

        # 写死未下单，已下单的走另一个接口
        # if prize_status > -1:
        #     condition += f" and prize_status={prize_status}"
        if prize_type > -1:
            condition.add_condition("prize_type=%s")
            params.append(prize_type)
        if sale_status > -1:
            condition.add_condition("sale_status=%s")
            params.append(sale_status)
        if ip_id > 0:
            condition.add_condition("ip_id=%s")
            params.append(ip_id)
        if is_open_buy_back > -1:
            condition.add_condition("is_open_buy_back=%s")
            params.append(is_open_buy_back)

        prize_roster_ex_list, total = prize_roster_ex_model.get_dict_page_list(field, page_index, page_size, condition.to_string(), "", order_by, params)
        # if prize_roster_ex_list:
        #     where_prize_order = SevenHelper.get_condition_by_int_list("id", [prize_info["prize_order_id"] for prize_info in prize_roster_ex_list])
        #     prize_order_list = prize_order_model.get_dict_list(where_prize_order)

        #     for prize_roster in prize_roster_ex_list:
        #         # 删除自动回购倒计时
        #         if prize_status == 1:
        #             prize_roster["automatic_buy_back_end_date"] = "1900-01-01 00:00:00"
        #         prize_order_id = prize_roster["prize_order_id"]
        #         for prize_order in prize_order_list:
        #             if prize_order["id"] == prize_order_id:
        #                 prize_roster["prize_order"] = prize_order
        #                 break

        page_info = PageInfo(page_index, page_size, total, prize_roster_ex_list)

        # 计算回购信息
        # buy_back_total_count = 0  #回购总数量
        # buy_back_total_integral = 0  #回购总积分
        # if prize_status == 0 and is_open_buy_back:
        #     buy_back_total_count = prize_roster_ex_model.get_total(condition, params=params)
        #     buy_back_total_integral = prize_roster_ex_model.get_dict(condition, field="SUM(buy_back_integral) AS buy_back_total_integral", params=params)["buy_back_total_integral"]
        # page_info.buy_back_total_count = buy_back_total_count
        # page_info.buy_back_total_integral = buy_back_total_integral if buy_back_total_integral else 0

        return self.response_json_success(page_info)


class PrizeOrderHandler(ClientBaseHandler):
    """
    :description: 获取用户下单列表
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 获取用户下单列表
        :param act_id：活动id
        :param tb_user_id：用户id
        :param page_index：页索引
        :param page_size：页大小
        :return: 
        :last_editors: HuangJingCan
        """
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 5)
        act_id = self.get_param_int("act_id")
        user_id = self.get_param_int("tb_user_id")

        prize_roster_ex_model = PrizeRosterExModel(context=self)
        prize_order_model = PrizeOrderModel(context=self)

        condition = "act_id=%s and user_id=%s"
        params = [act_id, user_id]
        order_by = "create_date desc"

        prize_order_list, total = prize_order_model.get_dict_page_list("*", page_index, page_size, condition, "", order_by, params)
        if prize_order_list:
            where_prize_roster = SevenHelper.get_condition_by_int_list("order_no", [prize_order["order_no"] for prize_order in prize_order_list])
            field = "order_no,id,prize_id,prize_name,prize_title,prize_pic,prize_status,tag_id,yfs_grade,yfs_key_name,sale_status,is_open_buy_back,buy_back_integral,automatic_buy_back_days,automatic_buy_back_end_date,create_date"
            prize_roster_list = prize_roster_ex_model.get_dict_list(where_prize_roster, order_by="id desc", field=field)

            for prize_order in prize_order_list:
                order_no = prize_order["order_no"]
                prize_order["prize_list"] = []
                for prize_roster in prize_roster_list:
                    if prize_roster["order_no"] == order_no:
                        prize_order["prize_list"].append(prize_roster)

        page_info = PageInfo(page_index, page_size, total, prize_order_list)

        return self.response_json_success(page_info)


class SubmitPrizeOrderHandler(ClientBaseHandler):
    """
    :description: 奖品订单提交
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 奖品订单提交
        :param act_id：活动id
        :param login_token：登录令牌
        :param user_prize_ids：用户奖品id串（逗号隔开，不传默认全部下单）
        :param real_name：用户名
        :param telephone：联系电话
        :param province：所在省
        :param city：所在市
        :param county：所在区
        :param street：所在街道
        :param address：收货地址
        :return 
        :last_editors: HuangJingCan
        """
        app_id = self.get_source_app_id()
        open_id = self.get_open_id()
        user_id = self.get_param_int("tb_user_id")
        act_id = self.get_param_int("act_id")
        login_token = self.get_param("login_token")
        user_prize_ids = self.get_param("user_prize_ids")
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        province = self.get_param("province")
        city = self.get_param("city")
        county = self.get_param("county")
        street = self.get_param("street")
        address = self.get_param("address")
        now_date = self.get_now_datetime()

        #请求太频繁限制
        if self.check_continue_request("SubmitPrizeOrder_Post_", app_id, open_id) == False:
            return self.response_json_error("HintMessage", "哎呀~当前操作人数过多")

        prize_roster_model = PrizeRosterExModel(context=self)
        prize_order_model = PrizeOrderModel(context=self)
        asset_base_model = AssetBaseModel(context=self)
        user_base_model = UserBaseModel(context=self)
        # user_info_ex_model = UserInfoExModel(context=self)

        user_info = user_base_model.get_user_info_dict(app_id, act_id, user_id)
        if not user_info:
            return self.response_json_error("NoUser", "对不起，用户不存在")
        if open_id != user_info["open_id"]:
            return self.response_json_error("ErrorUser", "对不起，用户不存在")
        if user_info["user_state"] == 1:
            return self.response_json_error("UserState", "对不起，你是黑名单用户,无法下单")
        if user_info["login_token"] != login_token:
            return self.response_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法下单")
        if not user_info["user_nick"]:
            return self.response_json_error("ErrorUserNick", "对不起，用户未授权")

        # 获取奖品
        params = [user_id, act_id]
        condition = ConditionWhere()
        condition.add_condition("user_id=%s and act_id=%s and prize_status=0 and (prize_type=5 and sale_status=1 or prize_type=1)")
        if user_prize_ids:
            condition.add_condition(SevenHelper.get_condition_in("id", user_prize_ids))
        else:
            return self.response_json_error("NoNeedSubmitPrize1", "对不起，没有未提交订单的奖品")

        prize_roster_dict_list = prize_roster_model.get_dict_list(condition.to_string(), limit="50", order_by="id desc", params=params)
        if len(prize_roster_dict_list) == 0:
            return self.response_json_error("NoNeedSubmitPrize2", "对不起，没有未提交订单的奖品")
        if len(prize_roster_dict_list) > 50:
            return self.response_json_error("ExceedSubmitLimit", "对不起，不能一次下单超过50件")

        # 没有选择sku下单功能
        # 奖品总金额价格
        # prize_price_sum = 0
        # # 判断是否有未选择sku奖品
        # for prize_roster in prize_roster_dict_list:
        #     prize_price_sum += prize_roster["prize_price"]
        #     if prize_roster["is_sku"] and (not prize_roster["sku_id"] or not prize_roster["sku_name"]):
        #         self.logging_link_error("NoSelectSku:" + str(prize_roster))
        #         return self.response_json_error("NoSelectSku", f"存在已选择的奖品未选择sku，无法进行下单操作")

        #1.0暂无运费功能
        # # 获取用户运费券
        # freight_voucher_value = 0  # 剩余运费券数量
        # user_asset_list = asset_base_model.get_user_asset_list(app_id, act_id, user_id, 101)
        # if len(user_asset_list) > 0:
        #     freight_voucher_value = user_asset_list[0]["asset_value"]
        # # 判断是否需要运费
        # is_freight_free = 1
        # freight_price = 0
        # config_freight = config_freight_model.get_dict("act_id=%s", params=act_id)
        # if config_freight and config_freight["freight_goods_id"]:
        #     # 无条件包邮
        #     if config_freight["is_freight_free"] and str(config_freight["freight_free_start_date"]) <= str(now_date) and str(now_date) <= str(config_freight["freight_free_end_date"]):
        #         pass
        #     # 判断是否开启满件数包邮
        #     elif config_freight["is_open_freight_free_num"] and config_freight["freight_free_num"] <= len(prize_roster_dict_list):
        #         pass
        #     # 判断是否开启满金额包邮
        #     elif config_freight["is_open_freight_free_price"] and (config_freight["freight_free_price"] <= prize_price_sum):
        #         pass
        #     # 不满包邮条件,扣除运费券
        #     elif freight_voucher_value <= 0:
        #         return self.response_json_error("NoFreightVoucher", "对不起，运费券不足")
        #     else:
        #         is_freight_free = 0
        #         freight_price = config_freight["freight_price"]
        #         #等待添加唯一标识(source_type：来源类型（1-购买2-任务3-手动配置4-抽奖5-回购 101-下单）)
        #         invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, 0, user_id, user_info["open_id"], user_info["user_nick"], 101, -1, "", 101, "", "", "下单消费运费券")
        #         if invoke_result_data.success == False:
        #             self.logging_link_error("下单消费运费券失败:" + str(invoke_result_data.__dict__))
        #             return self.response_json_error("FailFreight", "对不起，运费券使用失败")

        prize_order = PrizeOrder()
        prize_order.order_no = self.create_order_id()
        prize_order.app_id = app_id  # 应用标识
        prize_order.act_id = act_id  # 活动标识
        prize_order.user_id = user_id  # 用户标识
        prize_order.open_id = open_id  # open_id
        prize_order.user_nick = user_info["user_nick"]  # 用户昵称
        prize_order.real_name = real_name  # 真实姓名
        prize_order.telephone = telephone  # 手机号码
        prize_order.province = province  # 所在省
        prize_order.city = city  # 所在市
        prize_order.county = county  # 所在区
        prize_order.street = street  # 所在街道
        prize_order.address = address  # 收货地址
        prize_order.order_status = 0  # 订单状态（-1未付款-2付款中0未发货1已发货2不予发货3已退款4交易成功）
        prize_order.create_date = now_date  # 创建时间
        prize_order.create_month = SevenHelper.get_now_month_int()  # 创建月
        prize_order.create_day = SevenHelper.get_now_day_int()  # 创建天
        prize_order_id = prize_order_model.add_entity(prize_order)

        #更新用户奖品订单
        prize_roster_where = SevenHelper.get_condition_by_int_list("id", [i["id"] for i in prize_roster_dict_list])
        prize_roster_model.update_table("prize_order_id=%s,order_no=%s,prize_status=1,modify_date=%s", prize_roster_where, params=[prize_order_id, prize_order.order_no, now_date])
        # prize_roster_ex_model.update_table("prize_order_id=%s,prize_status=1,modify_date=%s", prize_roster_where, params=[prize_order_id, now_date])

        return self.response_json_success(prize_order)


class ChoicePrizeSkuHandler(ClientBaseHandler):
    """
    :description: 选择奖品sku -- 暂时没有该功能
    """
    @filter_check_params("act_id,user_prize_id,tb_user_id")
    def get_async(self):
        """
        :description: 选择奖品sku
        :param act_id：活动id
        :param login_token：登录令牌
        :param user_prize_id：用户奖品id
        :param sku_id：sku_id
        :param sku_name：选择的sku属性名
        :return 
        :last_editors: HuangJingCan
        """
        app_id = self.get_source_app_id()
        open_id = self.get_open_id()
        user_id = self.get_param_int("tb_user_id")
        act_id = self.get_param_int("act_id")
        user_prize_id = self.get_param_int("user_prize_id")
        sku_name = self.get_param("sku_name")
        login_token = self.get_param("login_token")
        sku_id = self.get_param("sku_id")

        #请求太频繁限制
        if self.check_continue_request("ChoicePrizeSku_Post", app_id, open_id) == False:
            return self.response_json_error("HintMessage", "哎呀~当前操作人数过多")

        prize_roster_model = PrizeRosterExModel(context=self)
        user_base_model = UserBaseModel(context=self)

        user_info = user_base_model.get_user_info_dict(app_id, act_id, user_id)
        if not user_info:
            return self.response_json_error("NoUser", "对不起，用户不存在")
        if open_id != user_info["open_id"]:
            return self.response_json_error("ErrorUser", "对不起，用户不存在")
        if user_info["user_state"] == 1:
            return self.response_json_error("UserBlock", "对不起，你是黑名单用户,无法选择SKU")
        if user_info["login_token"] != login_token:
            return self.response_json_error("ErrorLoginToken", "对不起，帐号已在另一台设备登录,当前无法选择SKU")

        prize_roster_dict = prize_roster_model.get_dict_by_id(user_prize_id)
        if not prize_roster_dict:
            return self.response_json_error("NoUser", "对不起，未找到该奖品信息")
        #获取奖品sku信息
        # act_prize_sku = ActPrizeSkuModel(context=self).get_dict("act_id=%s and act_prize_id=%s and sku_id=%s", params=[act_id, prize_roster_dict["prize_id"], sku_id])
        # if not act_prize_sku or act_prize_sku["surplus"] <= 0:
        #     return self.reponse_json_error("NoUser", "对不起，该属性没有库存，请重新选择")
        try:
            #更新选择的sku信息
            prize_roster_model.update_table("sku_id=%s,sku_name=%s", "id=%s", params=[sku_id, sku_name, user_prize_id])
        except Exception as ex:
            self.logging_link_error("ChoicePrizeSkuHandler:" + str(ex))
            return self.response_json_error("NoLottery", "对不起，SKU选择异常")

        self.response_json_success()


class BuyBackPrizeHandler(ClientBaseHandler):
    """
    :description: 奖品主动回购获得积分
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 奖品主动回购获得积分
        :param act_id：活动id
        :param login_token：登录令牌
        :param user_prize_ids: 背包奖品ID列表 -1全部
        :return 
        :last_editors: HuangJingCan
        """
        app_id = self.get_source_app_id()
        open_id = self.get_open_id()
        user_id = self.get_param_int("tb_user_id")
        act_id = self.get_param_int("act_id")
        login_token = self.get_param("login_token")
        user_prize_ids = self.get_param("user_prize_ids")
        now_date = self.get_now_datetime()

        #请求太频繁限制
        if self.check_continue_request("SubmitPrizeOrder_Post_", app_id, open_id) == False:
            return self.response_json_error("HintMessage", "哎呀~当前操作人数过多")

        act_info_model = ActInfoExModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)
        asset_base_model = AssetBaseModel(context=self)
        user_info_model = UserInfoExModel(context=self)
        user_base_model = UserBaseModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        user_info = user_base_model.get_user_info_dict(app_id, act_id, user_id)
        if not user_info:
            return self.response_json_error("NoUser", "对不起，用户不存在")
        if open_id != user_info["open_id"]:
            return self.response_json_error("ErrorUser", "对不起，用户不存在")
        if user_info["user_state"] == 1:
            return self.response_json_error("UserState", "对不起，你是黑名单用户,无法回购")
        if user_info["login_token"] != login_token:
            return self.response_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法回购")
        if not user_info["user_nick"]:
            return self.response_json_error("ErrorUserNick", "对不起，用户未授权")

        # 判断回购总开关有没开启
        dependency_key = business_base_model.get_cache_key_act_info(act_id)
        act_info = act_info_model.get_cache_dict_by_id(act_id, dependency_key=dependency_key, cache_expire=1800)
        # act_info = act_info_model.get_dict_by_id(act_id)
        if not act_info or not act_info["is_release"] or act_info["is_del"]:
            return self.response_json_error("NoAct1", "对不起，当前活动暂未开启，无法进行回购~")
        if not act_info["is_open_buy_back"]:
            return self.response_json_error("NoOpenBuyBack", "对不起，当前活动无法回购~")

        # 获取奖品
        params = [user_id, act_id]
        condition = ConditionWhere()
        condition.add_condition("user_id=%s and act_id=%s and prize_status=0 and is_open_buy_back=1 and (prize_type=5 and sale_status=1 or prize_type=1)")
        if user_prize_ids:
            condition.add_condition(SevenHelper.get_condition_in("id", user_prize_ids))
        else:
            return self.response_json_error("NoBuyBackPrize1", "对不起，未选择回购的奖品")

        prize_roster_ex_dict_list = prize_roster_ex_model.get_dict_list(condition.to_string(), limit="50", params=params)
        if len(prize_roster_ex_dict_list) == 0:
            return self.response_json_error("NoBuyBackPrize2", "对不起，没有选择回购的奖品")

        # 计算回购总积分
        asset_value = 0
        prize_roster_where = SevenHelper.get_condition_by_int_list("id", [i["id"] for i in prize_roster_ex_dict_list])
        for prize_roster_ex in prize_roster_ex_dict_list:
            asset_value += prize_roster_ex["buy_back_integral"]

        #等待添加唯一标识
        invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, 0, user_id, user_info["open_id"], user_info["user_nick"], 2, asset_value, "", 5, "", "", "手动回购")
        if invoke_result_data.success == False:
            self.logging_link_error("FailBuyBack:" + str(user_prize_ids))
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        else:
            user_info_model.update_table("buy_back_integral=buy_back_integral+%s,buy_back_num=buy_back_num+%s", "id=%s", [asset_value, len(prize_roster_ex_dict_list), user_info["id"]])
        #更新用户奖品订单
        prize_roster_ex_model.update_table("prize_status=2,modify_date=%s,buy_back_date=%s", prize_roster_where, params=[now_date, now_date])

        return self.response_json_success(asset_value)


class PresalePrizeNoticeHandler(ClientBaseHandler):
    """
    :description:预售奖品开售通知
    """
    @filter_check_params("act_id,tb_user_id")
    def get_async(self):
        """
        :description: 预售奖品开售通知
        :param act_id：活动id
        :param tb_user_id：用户id
        :return: 
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        user_id = self.get_param_int("tb_user_id")

        prize_roster_ex_model = PrizeRosterExModel(context=self)

        condition = "user_id=%s and act_id=%s and is_del=0 and prize_status=0 and prize_type=5 and sale_status=1 and have_presale_prize_notice=0"
        params = [user_id, act_id]
        order_by = "id desc"
        field = "prize_name,prize_pic,yfs_key_name"

        # 获取奖品
        prize_roster_ex_list = prize_roster_ex_model.get_dict_list(condition, order_by=order_by, limit="50", field=field, params=params)
        prize_roster_ex_model.update_table("have_presale_prize_notice=1", condition, params)

        return self.response_json_success(prize_roster_ex_list)


class SpecialPrizeNoticeHandler(ClientBaseHandler):
    """
    :description: 特殊奖品发放通知
    """
    @filter_check_params("act_id,tb_user_id,module_id")
    def get_async(self):
        """
        :description: 特殊奖品发放通知
        :param act_id：活动id
        :param tb_user_id：用户id
        :param module_id：机台id
        :return: 
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        user_id = self.get_param_int("tb_user_id")
        module_id = self.get_param_int("module_id")

        prize_roster_ex_model = PrizeRosterExModel(context=self)

        condition = "user_id=%s and module_id=%s and is_del=0 and prize_status=0 and yfs_type in (2,3) and have_special_prize_notice=0"
        params = [user_id, module_id]
        order_by = "id desc"
        field = "id,prize_name,prize_pic,yfs_key_name"

        # 获取奖品
        prize_roster_ex_list = prize_roster_ex_model.get_dict_list(condition, order_by=order_by, limit="50", field=field, params=params)

        return self.response_json_success(prize_roster_ex_list)


class UpdateSpecialPrizeNoticeHandler(ClientBaseHandler):
    """
    :description: 特殊奖品发放通知更新
    """
    @filter_check_params("act_id,prize_roster_id")
    def get_async(self):
        """
        :description: 特殊奖品发放通知
        :param act_id：活动id
        :param prize_roster_id: 背包奖品id
        :return: 
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        prize_roster_id = self.get_param_int("prize_roster_id")

        prize_roster_ex_model = PrizeRosterExModel(context=self)

        # 获取奖品
        prize_roster_ex_model.update_table("have_special_prize_notice=1", "id=%s", prize_roster_id)

        return self.response_json_success()