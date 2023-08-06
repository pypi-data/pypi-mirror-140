# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-06-02 13:44:17
@LastEditTime: 2022-02-22 14:41:45
@LastEditors: ChenCheng
:description: 奖品相关（包含箱数相关）接口
"""
from copy import deepcopy
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.libs.customize.oss2_helper import *
from seven_cloudapp_frame.models.seven_model import PageInfo

from seven_cloudapp_frame.models.db_models.act.act_prize_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *
from seven_cloudapp_frame.models.launch_base_model import LaunchBaseModel

from seven_cloudapp_ndjyfs.models.enum import *
from seven_cloudapp_ndjyfs.models.business_base_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_module_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.prize.prize_roster_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_senior_config_model import *


class PrizeHandler(ClientBaseHandler):
    """
    :description: 奖品保存
    """
    @filter_check_params("module_id")
    def post_async(self):
        """
        :description: 奖品保存
        :param prize_id：奖品id
        :param module_id: 机台id
        :param prize_type：奖品类型（1现货2优惠券3红包4参与奖5预售） 除新建之外，不支持修改奖品类型，直接传0
        :param sale_status：发售状态0未发售1已发售 预售奖品才传， 未开启高级功能不传  ---  发售状态不在奖品保存页做修改
        :param is_sku：是否开启sku 高级功能，未开启高级功能不传
        :param yfs_type：奖品等级类型 1普通2特殊3叠叠乐
        :param yfs_grade：一番赏类型（"First赏","A赏"...）
        :param sort_index：排序号
        :param prize_pic：奖品图片
        :param goods_id：商品id
        :param goods_code：商家编码
        :param prize_name：奖品名称
        :param prize_title：奖品标题
        :param prize_price：奖品价格
        :param probability：权重
        :param surplus：剩余库存
        :param prize_detail_json：奖品详情图
        :param is_open_prize_limit：是否开启中奖限制
        :param prize_limit：中奖限制
        :param is_senior_ability: 是否开启高级概率
        :param senior_ability_config: 高级功能配置（List：type_id类型id:1奖品锁定2强制出奖，is_open:是否开启，lock_count:限制数量，unlock_count:解封数量）
        :param is_open_buy_back：是否开启奖品回购, 未开启高级功能不传
        :param buy_back_integral：回购可获得积分
        :param first_open_threshold：First发赏阈值  未开启高级功能不传
        :param last_open_threshold：Las发赏阈值, 未开启高级功能不传
        :param random_open_start：全局赏发赏开始区间, 未开启高级功能不传
        :param random_open_end：全局赏发赏结束区间, 未开启高级功能不传
        :param dd_open_step：叠叠赏阶段, 未开启高级功能不传
        :param dd_open_threshold：叠叠赏发赏区间, 未开启高级功能不传
        :return: response_json_success
        :last_editors: HuangJingCan
        """
        prize_id = self.get_param_int("prize_id")
        module_id = self.get_param_int("module_id")
        prize_type = self.get_param_int("prize_type", 1)
        sort_index = self.get_param_int("sort_index", 1)
        # sale_status = self.get_param_int("sale_status") # 发售状态不在奖品保存页做修改
        is_sku = self.get_param_int("is_sku")
        yfs_type = self.get_param_int("yfs_type", 1)
        yfs_grade = self.get_param("yfs_grade")
        prize_name = self.get_param("prize_name")
        prize_title = self.get_param("prize_title")
        prize_pic = self.get_param("prize_pic")
        prize_detail_json = self.get_param("prize_detail_json")
        goods_id = self.get_param("goods_id")
        goods_code = self.get_param("goods_code")
        prize_price = float(self.get_param("prize_price", 0.00))
        tag_id = self.get_param_int("tag_id")
        probability = self.get_param_int("probability")
        surplus = self.get_param_int("surplus")
        is_open_prize_limit = self.get_param_int("is_open_prize_limit")
        prize_limit = self.get_param_int("prize_limit")
        is_senior_ability = self.get_param_int("is_senior_ability")
        senior_ability_config = self.get_param("senior_ability_config")
        is_open_buy_back = self.get_param_int("is_open_buy_back")
        buy_back_integral = self.get_param_int("buy_back_integral")
        first_open_threshold = self.get_param_int("first_open_threshold")
        last_open_threshold = self.get_param_int("last_open_threshold")
        random_open_start = self.get_param_int("random_open_start")
        random_open_end = self.get_param_int("random_open_end")
        dd_open_step = self.get_param_int("dd_open_step")
        dd_open_threshold = self.get_param_int("dd_open_threshold")
        # is_release = self.get_param_int("is_release", 1)
        sku_json = self.get_param("sku_json")
        now_time = self.get_now_datetime()

        # self.logging_link_error(self.request.uri + "-PrizeHandler-保存奖品" + str(self.request_params))

        act_prize_model = ActPrizeModel(context=self)
        act_prize_ex_model = ActPrizeExModel(context=self)
        prize_roster_model = PrizeRosterModel(context=self)
        prize_roster_ex_model = PrizeRosterExModel(context=self)
        act_prize_senior_config_model = ActPrizeSeniorConfigModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        #获取机台信息
        act_module_ex_model = ActModuleExModel(context=self)
        act_module_ex = act_module_ex_model.get_entity_by_id(module_id)
        if not act_module_ex or act_module_ex.is_del == 1:
            return self.response_json_error("NoMachine", "对不起，找不到此机台")
        if act_module_ex.is_release == 1:
            return self.response_json_error("NoExist", "对不起，机台未下架，无法删除奖品")

        app_id = act_module_ex.app_id
        act_id = act_module_ex.act_id
        ip_id = act_module_ex.ip_id
        module_id = act_module_ex.id

        act_prize = None
        act_prize_ex = None
        act_prize_senior_config = None
        old_act_prize_ex = None
        if prize_id > 0:
            act_prize = act_prize_model.get_entity_by_id(prize_id)
            act_prize_ex = act_prize_ex_model.get_entity_by_id(prize_id)
            act_prize_senior_config = act_prize_senior_config_model.get_entity("prize_id=%s", params=prize_id)
        if not act_prize_ex:
            act_prize = ActPrize()
            act_prize_ex = ActPrizeEx()
        else:
            old_act_prize_ex = deepcopy(act_prize_ex)
        if not act_prize_senior_config:
            act_prize_senior_config = ActPrizeSeniorConfig()

        #旧商品id
        old_goods_id = act_prize_ex.goods_id

        act_prize_ex.app_id = app_id
        act_prize_ex.act_id = act_id
        act_prize_ex.ip_id = ip_id
        act_prize_ex.module_id = module_id
        # if prize_type == 5:
        #     act_prize.sale_status = sale_status
        act_prize_ex.prize_name = prize_name
        act_prize_ex.prize_title = prize_title
        act_prize_ex.prize_pic = prize_pic
        act_prize_ex.prize_detail_json = prize_detail_json if prize_detail_json != "" else json.dumps([])
        act_prize_ex.goods_id = goods_id
        old_goods_code = act_prize_ex.goods_code
        act_prize_ex.goods_code = goods_code
        act_prize_ex.prize_type = prize_type
        act_prize_ex.prize_price = prize_price
        act_prize_ex.tag_id = tag_id
        act_prize_ex.probability = probability if yfs_type == 1 else 0
        act_prize_ex.prize_limit = prize_limit
        act_prize_ex.sort_index = sort_index
        act_prize_ex.is_del = 0  # 是否删除（1是0否）
        # act_prize.is_release = is_release
        act_prize_ex.modify_date = now_time
        # 扩展字段
        act_prize_ex.is_open_prize_limit = is_open_prize_limit  # 是否开启中奖限制
        if prize_id > 0 and act_prize_ex.yfs_type in (2, 3) and act_prize_ex.yfs_grade != yfs_grade:
            return self.response_json_error("ErrorUpdate", "对不起，特殊赏无法修改赏品等级")
        act_prize_ex.yfs_grade = yfs_grade  # 一番赏等级
        act_prize_ex.yfs_key_name = business_base_model.get_yfs_key_name(yfs_grade)  # 一番赏标识名称
        #高级功能
        act_prize_ex.is_sku = is_sku
        act_prize_ex.sku_json = sku_json
        act_prize_ex.is_senior_ability = is_senior_ability
        act_prize_ex.senior_ability_config = senior_ability_config
        act_prize_ex.is_open_buy_back = is_open_buy_back
        act_prize_ex.buy_back_integral = buy_back_integral
        if yfs_grade == "First赏":
            act_prize_ex.first_open_threshold = first_open_threshold
        if yfs_grade == "Last赏":
            act_prize_ex.last_open_threshold = last_open_threshold
        if yfs_grade == "随机赏":
            act_prize_ex.random_open_start = random_open_start
            act_prize_ex.random_open_end = random_open_end
        if yfs_type == 3:
            if dd_open_threshold < surplus:
                return self.response_json_error("ErrorThreshold", f"对不起，叠叠赏库存不能大于发赏区间")
            act_prize_ex.dd_open_step = dd_open_step
            act_prize_ex.dd_open_threshold = dd_open_threshold
        #生成奖品高级配置
        act_prize_senior_config.act_id = act_id
        act_prize_senior_config.app_id = app_id
        act_prize_senior_config.module_id = module_id
        act_prize_senior_config.modify_date = now_time
        # 强制概率
        if is_senior_ability == 1 and senior_ability_config:
            senior_ability_config_list = self.json_loads(senior_ability_config)
            old_senior_ability_config_list = self.json_loads((old_act_prize_ex.senior_ability_config if old_act_prize_ex and old_act_prize_ex.senior_ability_config else "[]"))
            for i in range(len(senior_ability_config_list)):
                old_senior_ability_config = [old_senior_ability_config for old_senior_ability_config in old_senior_ability_config_list if old_senior_ability_config["type_id"] == senior_ability_config_list[i]["type_id"]]
                #首次开启高级配置
                if not old_senior_ability_config or old_senior_ability_config[0]["lock_count"] != senior_ability_config_list[i]["lock_count"]:
                    if int(senior_ability_config_list[i]["type_id"]) == PrizeSeniorConfigType.奖品锁定.value:
                        #重置剩余锁定数
                        act_prize_senior_config.surplus_lock_count = senior_ability_config_list[i]["lock_count"]
                    if int(senior_ability_config_list[i]["type_id"]) == PrizeSeniorConfigType.强制出奖.value:
                        #重置必中剩余数
                        act_prize_senior_config.must_surplus_count = senior_ability_config_list[i]["lock_count"]

        # 基础表赋值---投放使用
        act_prize.app_id = act_prize_ex.app_id
        act_prize.act_id = act_prize_ex.act_id
        act_prize.goods_id = act_prize_ex.goods_id
        act_prize.goods_code = act_prize_ex.goods_code
        act_prize.module_id = act_prize_ex.module_id
        act_prize.prize_name = act_prize_ex.prize_name
        act_prize.prize_title = act_prize_ex.prize_title

        if prize_id > 0:
            # 增量添加库存
            update_surplus = abs(surplus - act_prize_ex.surplus) if act_prize_ex.yfs_type == 1 else 0
            if update_surplus > 0:
                if act_prize_ex.yfs_type in (2, 3):
                    return self.response_json_error("ErrorChange", f"对不起，{act_prize_ex.yfs_grade}不可修改奖品库存")
                if surplus > act_prize_ex.surplus:
                    act_prize_ex.prize_total += update_surplus
                else:
                    act_prize_ex.prize_total -= update_surplus
                act_prize_ex.surplus = surplus

            # 更新商家编码，同步修改所有奖品
            if old_goods_code != goods_code:
                prize_roster_model.update_table("goods_code=%s", f"prize_id={prize_id}", params=[goods_code])
                prize_roster_ex_model.update_table("goods_code=%s", f"prize_id={prize_id}", params=[goods_code])

            act_prize_model.update_entity(act_prize)
            act_prize_ex_model.update_entity(act_prize_ex)

            self.create_operation_log(OperationType.update.value, act_prize_ex.__str__(), "PrizeHandler", self.json_dumps(old_act_prize_ex.__dict__), self.json_dumps(act_prize_ex.__dict__))
        else:
            act_prize_ex.yfs_type = yfs_type  # 一番赏等级类型1普通2特殊3叠叠乐
            act_prize_ex.create_date = now_time
            act_prize_ex.surplus = surplus if surplus > 0 else 0
            act_prize_ex.hand_out = 0
            act_prize_ex.prize_total = act_prize_ex.surplus
            act_prize_ex.sale_status = 0 if prize_type == 5 else 1  # 发售状态0未发售1已发售
            act_prize.id = act_prize_model.add_entity(act_prize)
            act_prize_ex.id = act_prize.id
            act_prize_ex_model.add_entity(act_prize_ex)

            self.create_operation_log(OperationType.add.value, act_prize_ex.__str__(), "PrizeHandler", None, self.json_dumps(act_prize_ex.__dict__))

        #保存奖品高级配置表
        if act_prize_senior_config.id > 0:
            act_prize_senior_config_model.update_entity(act_prize_senior_config)
        else:
            act_prize_senior_config.prize_id = act_prize.id
            act_prize_senior_config_model.add_entity(act_prize_senior_config)

        # 删除依赖建
        act_prize_senior_config_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_senior_config_list(act_id, module_id))
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_module_id(module_id))
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_act_id(act_id))

        #投放商品处理
        launch_base_model = LaunchBaseModel(context=self)
        launch_base_model.add_launch_goods(app_id, act_id, goods_id, old_goods_id, "1,2")

        return self.response_json_success(act_prize_ex.id)


class PrizeListHandler(ClientBaseHandler):
    """
    :description: 奖品列表
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description: 获取奖品列表
        :param module_id: 机台id
        :param page_index：页索引
        :param page_size：页大小
        :return: list
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)

        prize_all_count = 0  # 总奖品数
        prize_surplus_count = 0  # 库存不足数
        prize_lottery_count = 0  # 可抽中数
        prize_sum_probability = 0  # 奖品总权重
        prize_surplus_sum = 0  # 奖品库存剩余总数量

        act_prize_ex_model = ActPrizeExModel(context=self)
        act_prize_senior_config_model = ActPrizeSeniorConfigModel(context=self)

        # 计算奖品页总体数据
        prize_all_count = act_prize_ex_model.get_total("module_id=%s and is_del=0", params=module_id)
        prize_surplus_count = act_prize_ex_model.get_total("module_id=%s and is_del=0 and is_release=1 and yfs_type=1 and surplus<=0", params=module_id)
        field = "CAST(SUM(probability) AS SIGNED) AS prize_sum_probability,CAST(SUM(surplus) AS SIGNED) AS prize_surplus_sum, CAST(SUM(yfs_type) AS SIGNED) AS prize_lottery_count"
        prize_sum_probability_dict = act_prize_ex_model.get_dict("module_id=%s and is_del=0 and is_release=1 and yfs_type=1 and surplus>0 and probability>0", field=field, params=module_id)
        prize_sum_probability = prize_sum_probability_dict["prize_sum_probability"] if prize_sum_probability_dict["prize_sum_probability"] else 0
        # prize_surplus_sum = prize_sum_probability_dict["prize_surplus_sum"] if prize_sum_probability_dict["prize_surplus_sum"] else 0
        prize_lottery_count = prize_sum_probability_dict["prize_lottery_count"] if prize_sum_probability_dict["prize_lottery_count"] else 0

        # 获取奖品列表
        act_prize_list, total = act_prize_ex_model.get_dict_page_list("*", page_index, page_size, "module_id=%s AND is_del=0", "", order_by="sort_index desc", params=[module_id])
        if act_prize_list:
            act_id = act_prize_list[0]["act_id"]
            #获取活动奖品高级配置列表
            act_prize_senior_config_list = act_prize_senior_config_model.get_dict_list("act_id=%s and module_id=%s", params=[act_id, module_id])
            for act_prize in act_prize_list:
                act_prize["chance"] = 0 # 概率
                act_prize["status"] = 0 # 奖池状态标识
                act_prize["status_name"] = "不可被抽中"  # 奖池状态说明
                act_prize["buy_back_status_name"] = f"{act_prize['buy_back_integral']}积分" if act_prize["is_open_buy_back"] else "未开启"  # 奖品回购状态说明

                if act_prize["prize_detail_json"]:
                    act_prize["prize_detail_json"] = self.json_loads(act_prize["prize_detail_json"])
                if act_prize["senior_ability_config"]:
                    act_prize["senior_ability_config"] = self.json_loads(act_prize["senior_ability_config"])
                if act_prize["is_release"]:
                    if act_prize["yfs_type"] == 1:
                        if act_prize["probability"] > 0 and act_prize["surplus"] > 0:
                            act_prize["chance"] = round(act_prize["probability"] / prize_sum_probability * 100, 2)
                            if act_prize["is_senior_ability"]:
                                act_prize["status"] = 0
                                act_prize["status_name"] = "高级功能配置错误，请重新配置"
                                senior_ability_config_list = act_prize["senior_ability_config"]
                                if senior_ability_config_list:
                                    for senior_ability_config in senior_ability_config_list:
                                        if int(senior_ability_config["is_open"]) == 1:
                                            if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.奖品锁定.value:
                                                # act_prize["status_name"] = f"剩余{senior_ability_config['lock_count']}时库存锁定，总库存最后{senior_ability_config['unlock_count'] }件解锁库存"
                                                # 锁定且未到解锁时机-不可抽出
                                                if act_prize["surplus"] <= senior_ability_config["lock_count"] and senior_ability_config["unlock_count"] < prize_surplus_sum:
                                                    act_prize["status"] = 0
                                                    act_prize["status_name"] = f"不可抽中:{prize_surplus_sum-senior_ability_config['unlock_count']}件后解锁（奖池剩余≤{senior_ability_config['unlock_count']}件）"
                                                else:
                                                    act_prize["status"] = 1
                                                    act_prize["status_name"] = f"锁定：当前奖品≤{senior_ability_config['lock_count']}件;解锁：总奖池≤{senior_ability_config['unlock_count']}件"
                                            elif int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.强制出奖.value:
                                                act_prize_senior_config = [act_prize_senior_config for act_prize_senior_config in act_prize_senior_config_list if act_prize_senior_config["prize_id"] == act_prize["id"]]
                                                if act_prize_senior_config:
                                                    act_prize_senior_config = act_prize_senior_config[0]
                                                    if act_prize_senior_config["is_lock"] == 1:
                                                        act_prize["status"] = 0
                                                        act_prize["status_name"] = f"不可抽中：{act_prize_senior_config['must_surplus_count']}件后可抽中（每{senior_ability_config['lock_count']}件出一件）"
                                                    else:
                                                        act_prize["status"] = 1
                                                        act_prize["status_name"] = f"{act_prize_senior_config['must_surplus_count']}件内必出一件"
                            else:
                                act_prize["status"] = 1
                                act_prize["status_name"] = "可被抽中"
                    else:
                        if act_prize["hand_out"] > 0:
                            act_prize["status"] = 0
                            act_prize["status_name"] = "已自动出奖"
                        else:
                            if act_prize["yfs_type"] == 3:
                                act_prize["status"] = 1
                                act_prize["status_name"] = f"阶段{ act_prize['dd_open_step']}解锁：已出奖品≥{ act_prize['dd_open_threshold']}件"
                            else:
                                act_prize["status"] = 1
                                act_prize["status_name"] = "等待自动出奖"



                # 由于反复横跳的策划，可能会在某个版本回归本段判断，故而保留
                # act_prize["status"] = 0 # 奖池状态标识
                # act_prize["status_name"] = "不可抽中" # 奖池状态说明
                # act_prize["must_status_name"] = "" # 强制概率状态说明
                # act_prize["surplus_lock_status_name"] = "" # 库存锁定状态说明
                # act_prize["special_DD_status_name"] = "" # 叠叠乐状态说明
                # if act_prize["is_release"]:
                #     if act_prize["yfs_type"] == 1 and act_prize["probability"] > 0 and act_prize["surplus"] > 0:
                #         act_prize["chance"] = round(act_prize["probability"] / prize_sum_probability * 100, 2)
                #         act_prize["status"] = 1
                #         act_prize["status_name"] = "可被抽中"
                #     elif act_prize["surplus"] > 0:
                #         act_prize["status"] = 2
                #         act_prize["status_name"] = "等待自动出奖"
                #     else:
                #         act_prize["status"] = 3
                #         act_prize["status_name"] = "已自动出奖"

                # if act_prize["yfs_type"] == 1:
                # if act_prize["is_senior_ability"]:
                #     senior_ability_config_list = act_prize["senior_ability_config"]
                #     if senior_ability_config_list:
                #         for senior_ability_config in senior_ability_config_list:
                #             if int(senior_ability_config["is_open"]) == 1:
                #                 if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.奖品锁定.value:
                #                     act_prize["surplus_lock_status_name"] = f"锁定：当前奖品≤{senior_ability_config['lock_count']}件;解锁：总奖池≤{senior_ability_config['unlock_count']}件"
                #                 if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.强制出奖.value:
                #                     act_prize["must_status_name"] = f"每{senior_ability_config['lock_count']}件出一件"
                #     else:
                #         act_prize["must_status_name"] = "高级功能配置错误，请重新配置"
                #         act_prize["surplus_lock_status_name"] = "高级功能配置错误，请重新配置"
                # else:
                #     act_prize["must_status_name"] = "未开启"
                #     act_prize["surplus_lock_status_name"] = "未开启"
                # elif act_prize["yfs_type"] == 3:
                #     act_prize["special_DD_status_name"] = f"阶段{ act_prize['dd_open_step']}解锁：已出奖品≥{ act_prize['dd_open_threshold']}件"

                # if prize_sum_probability and act_prize["is_release"] and act_prize["yfs_type"] == 1 and act_prize["probability"] > 0 and act_prize["surplus"] > 0:
                #     act_prize["chance"] = round(act_prize["probability"] / prize_sum_probability * 100, 2)
                #     if act_prize["is_senior_ability"]:
                #         senior_ability_config_list = act_prize["senior_ability_config"]
                #         if senior_ability_config_list:
                #             for senior_ability_config in senior_ability_config_list:
                #                 if int(senior_ability_config["is_open"]) == 1:
                #                     if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.奖品锁定.value:
                #                         act_prize["status_name"] = f"剩余{senior_ability_config['lock_count']}时库存锁定，总库存最后{senior_ability_config['unlock_count'] }件解锁库存"
                #                         # 锁定且未到解锁时机-不可抽出
                #                         if act_prize["surplus"] <= senior_ability_config["lock_count"] and senior_ability_config["unlock_count"] < prize_surplus_sum:
                #                             act_prize["status"] = 0
                #                             act_prize["status_name"] = f"不可抽中，{prize_surplus_sum-senior_ability_config['unlock_count']}件后解锁"
                #                             break
                #                     if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.强制出奖.value:
                #                         act_prize_senior_config = [act_prize_senior_config for act_prize_senior_config in act_prize_senior_config_list if act_prize_senior_config["prize_id"] == act_prize["id"]]
                #                         if act_prize_senior_config:
                #                             act_prize_senior_config = act_prize_senior_config[0]
                #                             if act_prize_senior_config["is_lock"] == 1:
                #                                 act_prize["status"] = 0
                #                                 act_prize["status_name"] = f"{act_prize_senior_config['must_surplus_count']}件后可抽中"
                #                             else:
                #                                 act_prize["status"] = 1
                #                                 act_prize["status_name"] = f"{act_prize_senior_config['must_surplus_count']}件内必出一件"
                #                             break
                #                         else:
                #                             act_prize["status"] = 0
                #                             act_prize["status_name"] = "高级功能配置错误，请重新配置"
                #         else:
                #             act_prize["status"] = 0
                #             act_prize["status_name"] = "高级功能配置错误，请重新配置"
                # else:
                #     act_prize["status"] = 0
                #     act_prize["status_name"] = "不可抽中"



        page_info = PageInfo(page_index, page_size, total, act_prize_list)
        page_info.prize_all_count = prize_all_count
        page_info.prize_surplus_count = prize_surplus_count
        page_info.prize_lottery_count = prize_lottery_count
        page_info.prize_sum_probability = prize_sum_probability

        return self.response_json_success(page_info)


class PrizeDelHandler(ClientBaseHandler):
    """
    :description: 删除奖品
    """
    @filter_check_params("module_id,prize_id")
    def get_async(self):
        """
        :description: 删除奖品
        :param module_id: 机台id
        :param prize_id：奖品id
        :return: response_json_success
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        prize_id = self.get_param_int("prize_id")
        modify_date = self.get_now_datetime()

        #获取机台信息
        act_module_ex_model = ActModuleExModel(context=self)
        act_module_ex = act_module_ex_model.get_entity_by_id(module_id)
        if not act_module_ex or act_module_ex.is_del == 1:
            return self.response_json_error("NoMachine", "对不起，找不到此机台")
        if act_module_ex.is_release == 1:
            return self.response_json_error("NoExist", "对不起，机台未下架，无法删除奖品")
        act_id = act_module_ex.act_id

        act_prize_model = ActPrizeModel(context=self)
        act_prize_ex_model = ActPrizeExModel(context=self)

        act_prize_model.update_table("modify_date=%s,is_del=1", "id=%s", params=[modify_date, prize_id])
        act_prize_ex_model.update_table("modify_date=%s,is_del=1", "id=%s", params=[modify_date, prize_id])

        # 删除依赖建
        business_base_model = BusinessBaseModel()
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_module_id(module_id))
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_act_id(act_id))

        self.create_operation_log(OperationType.delete.value, "act_prize_ex_tb", "PrizeDelHandler", None, prize_id)

        return self.response_json_success()


class PrizeReleaseHandler(ClientBaseHandler):
    """
    :description: 上下架奖品
    """
    @filter_check_params("module_id,prize_id")
    def get_async(self):
        """
        :description: 上下架奖品
        :param module_id: 机台id
        :param prize_id：奖品id
        :param is_release：0-下架，1-上架
        :return: 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        prize_id = self.get_param_int("prize_id")
        is_release = self.get_param_int("is_release")
        modify_date = self.get_now_datetime()

        #获取机台信息
        act_module_ex_model = ActModuleExModel(context=self)
        act_module_ex = act_module_ex_model.get_entity_by_id(module_id)
        if not act_module_ex or act_module_ex.is_del == 1:
            return self.response_json_error("NoMachine", "对不起，找不到此机台")
        if act_module_ex.is_release == 1:
            return self.response_json_error("NoExist", "对不起，机台未下架，无法删除奖品")
        act_id = act_module_ex.act_id

        act_prize_ex_model = ActPrizeExModel(context=self)
        act_prize_ex = act_prize_ex_model.get_entity_by_id(prize_id)
        if is_release == 1:
            if act_prize_ex.yfs_type == 2:
                condition = "module_id=%s and is_del=0 and is_release=1 and yfs_type=2 and yfs_grade=%s"
                params = [module_id, act_prize_ex.yfs_grade]
                if prize_id:
                    condition += " and id!=%s"
                    params.append(prize_id)
                have_yfs_grade = act_prize_ex_model.get_total(condition, params=params)
                if have_yfs_grade:
                    return self.response_json_error("HaveYfsGrade", f"对不起，{act_prize_ex.yfs_grade}已存在")
            elif act_prize_ex.yfs_type == 3:
                condition = "module_id=%s and is_del=0 and is_release=1 and yfs_type=3 and dd_open_step=%s"
                params = [module_id, act_prize_ex.dd_open_step]
                if prize_id:
                    condition += " and id!=%s"
                    params.append(prize_id)
                have_yfs_grade = act_prize_ex_model.get_total(condition, params=params)
                if have_yfs_grade:
                    return self.response_json_error("HaveYfsGrade", f"对不起，阶段{act_prize_ex.yfs_grade}叠叠赏已存在")

        act_prize_ex_model.update_table("is_release=%s,modify_date=%s", "id=%s", [is_release, modify_date, prize_id])
        act_prize_model = ActPrizeModel(context=self)
        act_prize_model.update_table("is_release=%s,modify_date=%s", "id=%s", [is_release, modify_date, prize_id])

        # 删除依赖建
        business_base_model = BusinessBaseModel()
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_module_id(module_id))
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_act_id(act_id))

        return self.response_json_success()


class PrizeSurplusHandler(ClientBaseHandler):
    """
    :description: 修改奖品库存
    """
    @filter_check_params("module_id,prize_id,surplus")
    def get_async(self):
        """
        :description: 修改奖品库存
        :param module_id: module_id
        :param prize_id: 奖品id
        :param surplus：剩余库存
        :return 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        prize_id = self.get_param_int("prize_id")
        surplus = self.get_param_int("surplus")
        modify_date = self.get_now_datetime()

        act_prize_ex_model = ActPrizeExModel(context=self)

        #获取机台信息
        act_module_ex_model = ActModuleExModel(context=self)
        act_module_ex = act_module_ex_model.get_entity_by_id(module_id)
        if not act_module_ex or act_module_ex.is_del == 1:
            return self.response_json_error("NoMachine", "对不起，找不到此机台")
        if act_module_ex.is_release == 1:
            return self.response_json_error("NoExist", "对不起，机台未下架，无法删除奖品")
        act_id = act_module_ex.act_id

        update_sql = "surplus=%s"
        where = f"id={prize_id}"
        params = [surplus]

        act_prize_ex = act_prize_ex_model.get_entity_by_id(prize_id)
        if act_prize_ex.yfs_type in (2, 3):
            return self.response_json_error("ErrorChange", f"对不起，{act_prize_ex.yfs_grade}不可修改奖品库存")

        act_prize = act_prize_ex_model.get_entity_by_id(prize_id)

        update_surplus = abs(surplus - act_prize.surplus)

        if update_surplus == 0:
            return self.response_json_success()

        if surplus > act_prize.surplus:
            act_prize.prize_total += update_surplus
        else:
            act_prize.prize_total -= update_surplus
        update_sql += ",prize_total=%s"
        params.append(act_prize.prize_total)

        act_prize.surplus = surplus

        act_prize_ex_model.update_table(update_sql, where, params)
        update_sql = f"modify_date='{str(modify_date)}'," + update_sql
        act_prize_ex_model.update_table(update_sql, where, params)

        # 删除依赖建
        business_base_model = BusinessBaseModel()
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_module_id(module_id))
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_act_id(act_id))

        return self.response_json_success()


class PrizeProbabilityHandler(ClientBaseHandler):
    """
    :description: 修改奖品权重
    """
    @filter_check_params("module_id,prize_id,probability")
    def get_async(self):
        """
        :description: 修改奖品权重
        :param module_id: module_id
        :param prize_id: 奖品id
        :param probability：权重
        :return 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        prize_id = self.get_param_int("prize_id")
        probability = self.get_param_int("probability")
        modify_date = self.get_now_datetime()

        act_prize_ex_model = ActPrizeExModel(context=self)

        #获取机台信息
        act_module_ex_model = ActModuleExModel(context=self)
        act_module_ex = act_module_ex_model.get_entity_by_id(module_id)
        if not act_module_ex or act_module_ex.is_del == 1:
            return self.response_json_error("NoMachine", "对不起，找不到此机台")
        if act_module_ex.is_release == 1:
            return self.response_json_error("NoExist", "对不起，机台未下架，无法删除奖品")
        act_id = act_module_ex.act_id

        act_prize_ex = act_prize_ex_model.get_entity_by_id(prize_id)
        if act_prize_ex.yfs_type in (2, 3):
            return self.response_json_error("ErrorChange", f"对不起，{act_prize_ex.yfs_grade}不可修改奖品权重")

        # act_prize = act_prize_model.get_entity_by_id(prize_id)
        # act_prize.probability = probability
        update_sql = "probability=%s"
        if probability == 0:
            update_sql += ",is_senior_ability=0"

        act_prize_ex_model.update_table("modify_date=%s,probability=%s", "id=%s", [modify_date, probability, prize_id])

        # 删除依赖建
        business_base_model = BusinessBaseModel()
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_module_id(module_id))
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_act_id(act_id))

        return self.response_json_success()


class UpdateGoodsCodeHandler(ClientBaseHandler):
    """
    :description: 更新商家编码
    """
    @filter_check_params("act_id,goods_code,prize_id")
    def get_async(self):
        """
        :description: 更新商家编码
        :param act_id：活动id
        :param prize_id：奖品id
        :param goods_code：商家编码
        :param old_goods_code：旧商家编码
        :return: response_json_success
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        prize_id = self.get_param_int("prize_id")
        goods_code = self.get_param("goods_code")
        old_goods_code = self.get_param("old_goods_code")

        condition = "act_id=%s AND prize_id=%s"
        params = [goods_code, act_id, prize_id]
        if old_goods_code:
            condition += " AND goods_code=%s"
            params.append(old_goods_code)

        act_prize_ex_model = ActPrizeExModel(context=self)
        act_prize = act_prize_ex_model.get_entity_by_id(prize_id)
        if not act_prize:
            return self.response_json_error("NoPrize", "对不起,未找到奖品信息")

        prize_roster_model = PrizeRosterModel(context=self)

        act_prize_ex_model.update_table("goods_code=%s", "id=%s", params=[goods_code, prize_id])
        result = prize_roster_model.update_table("goods_code=%s", condition, params)

        # 删除依赖建
        business_base_model = BusinessBaseModel()
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_module_id(act_prize.module_id))
        act_prize_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_act_id(act_prize.act_id))

        return self.response_json_success(result)


# ActPrizeExportHandler
class PrizeListExportHandler(ClientBaseHandler):
    """
    :description: 奖品列表导出
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description: 奖品列表导出
        :param module_id: module_id
        :return: 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")

        condition = "module_id=%s"
        params = [module_id]
        order_by = "id"

        act_prize_ex_model = ActPrizeExModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        # 生成数据，导出execl
        result_data = []  # 结果集
        page_list = act_prize_ex_model.get_dict_list(condition, order_by=order_by, params=params)
        if len(page_list) > 0:
            #订单奖品
            for page_info in page_list:
                data_row = {}
                data_row["奖品图片"] = page_info["prize_pic"]
                data_row["奖品短名称"] = page_info["prize_name"]
                data_row["奖品长名称"] = page_info["prize_title"]
                data_row["商家编码"] = page_info["goods_code"]
                data_row["奖品种类"] = business_base_model.get_yfs_type_name(page_info["yfs_type"])
                data_row["奖品类型"] = business_base_model.get_prize_type_name(page_info["prize_type"])
                data_row["奖品价值"] = str(page_info["prize_price"])
                data_row["奖品库存"] = page_info["surplus"]
                data_row["中奖权重"] = page_info["probability"]
                data_row["奖品回购积分"] = page_info["buy_back_integral"]
                data_row["强制概率"] = page_info["is_senior_ability"]
                data_row["库存锁定"] = page_info["is_senior_ability"]
                # data_row["创建时间"] = TimeHelper.datetime_to_format_time(page_info["create_date"])
                # data_row["是否发布"] = "未发布"
                # if page_info["is_release"] == 1:
                #     data_row["是否发布"] = "已发布"
                result_data.append(data_row)

        resource_path = ""
        #导入Excel
        if result_data:
            resource_path = OSS2Helper().export_excel(result_data)

        return self.response_json_success(resource_path)