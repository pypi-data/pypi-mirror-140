# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-29 09:40:42
@LastEditTime: 2022-02-23 11:08:24
@LastEditors: ChenCheng
:description: 机台（盒子）
"""
import decimal
from seven_cloudapp_frame.handlers.frame_base import *

from seven_cloudapp_frame.models.seven_model import PageInfo
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_module_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *
from seven_cloudapp_frame.models.db_models.price.price_gear_model import *
from seven_cloudapp_frame.models.db_models.skin.skin_info_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_orm_model import *

from seven_cloudapp_ndjyfs.models.enum import *
from seven_cloudapp_ndjyfs.models.business_base_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_senior_config_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_info_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_module_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_ex_model import *


class MachineHandler(ClientBaseHandler):
    """
    :description: 保存机台
    """
    @filter_check_params("app_id,act_id,module_name")
    def post_async(self):
        """
        :description: 保存机台
        :param module_id: 机台id
        :param act_id: 活动id
        :param app_id: app_id
        :param ip_id: ip_id
        :param module_name: 机台名称
        :param module_pic: 机台图片
        :param module_desc: 机台备注
        :param skin_id: 主题皮肤id
        :param module_type: 抽赏模式: 1次数2积分3一番赏4叠叠赏
        :param price_gear_id: 价格档位id
        :param sort_index: 排序
        :param continuous_lottery_times: 连抽次数
        :param single_lottery_integral: 单抽积分
        :param continuous_lottery_integral: 连抽积分
        :param continuous_lottery_integral_times: 连抽积分次数
        :param is_limit_lottery_times: 是否限制扭蛋次数(0-不限制1限制)
        :param price_single_lottery_limit: 价格单抽每日限制次数
        :param price_continuous_lottery_limit: 价格连抽每日限制次数
        :param integral_single_lottery_limit: 积分单抽每日限制次数
        :param integral_continuous_lottery_limit: 积分连抽每日限制次数
        :param is_open_all_lottery: 是否开启全收（0-未开启1-开启）
        :param all_lottery_count: 全收数量
        :param is_no_repeat_prize: 连抽奖品不重复：0-重复1-不重复
        :param is_automatic_buy_back: 是否开启自动回购：0关闭1开启
        :param automatic_buy_back_days: 自动回购天数
        :param is_surplus: 是否显示奖品库存：0-不显示1-显示
        :param is_chance: 是否显示奖品概率：0-不显示1-显示
        :param is_notice: 是否显示机台中奖弹幕：0-不显示1-显示
        :param start_date: 开始销售时间
        :param end_date: 结束销售时间
        :return: response_json_success
        :last_editors: HuangJingCan
        """
        app_id = self.get_app_id()
        act_id = self.get_param_int("act_id", 0)
        module_id = self.get_param_int("module_id", 0)
        ip_id = self.get_param_int("ip_id", 0)
        module_name = self.get_param("module_name")
        module_pic = self.get_param("module_pic")
        module_desc = self.get_param("module_desc")
        skin_id = self.get_param_int("skin_id", 0)
        module_type = self.get_param_int("module_type", 1)
        price_gear_id = self.get_param_int("price_gear_id", 0)
        sort_index = self.get_param_int("sort_index", 0)
        continuous_lottery_times = self.get_param_int("continuous_lottery_times", 0)
        single_lottery_integral = self.get_param_int("single_lottery_integral", 0)
        continuous_lottery_integral = self.get_param_int("continuous_lottery_integral", 0)
        continuous_lottery_integral_times = self.get_param_int("continuous_lottery_integral_times", 0)
        is_limit_lottery_times = self.get_param_int("is_limit_lottery_times", 0)
        single_lottery_limit = self.get_param_int("single_lottery_limit", 0)
        continuous_lottery_limit = self.get_param_int("continuous_lottery_limit", 0)
        is_open_all_lottery = self.get_param_int("is_open_all_lottery", 0)
        all_lottery_count = self.get_param_int("all_lottery_count", 0)
        is_no_repeat_prize = self.get_param_int("is_no_repeat_prize", 0)
        is_automatic_buy_back = self.get_param_int("is_automatic_buy_back", 0)
        automatic_buy_back_days = self.get_param_int("automatic_buy_back_days", 0)
        is_surplus = self.get_param_int("is_surplus", 1)
        is_chance = self.get_param_int("is_chance", 1)
        is_notice = self.get_param_int("is_notice", 1)
        start_date = self.get_param("start_date", "1900-01-01 00:00:00")
        end_date = self.get_param("end_date", "1900-01-01 00:00:00")
        now_time = self.get_now_datetime()

        if act_id <= 0:
            return self.response_json_error_params()

        module_info_ex = None
        module_info_ex_model = ActModuleExModel(context=self)
        price_gear_model = PriceGearModel(context=self)

        if module_id > 0:
            module_info_ex = module_info_ex_model.get_entity_by_id(module_id)

        is_add = False
        if not module_info_ex:
            is_add = True
            module_info_ex = ActModuleEx()
        if module_info_ex.is_release == 1:
            return self.response_json_error("Release", "对不起，机台上架状态，无法保存")

        old_module_info_ex = deepcopy(module_info_ex)

        module_info_ex.app_id = app_id
        module_info_ex.act_id = act_id
        module_info_ex.ip_id = ip_id
        module_info_ex.sort_index = sort_index
        module_info_ex.module_name = module_name
        module_info_ex.module_pic = module_pic
        module_info_ex.module_desc = module_desc
        module_info_ex.skin_id = skin_id
        module_info_ex.module_type = module_type
        module_info_ex.start_date = start_date
        module_info_ex.end_date = end_date
        # 价格挡位
        price_gear_price = 0.00
        if module_type == 2:
            price_gear_id = 0
        else:
            price_gear = price_gear_model.get_entity_by_id(price_gear_id)
            if price_gear and not price_gear.is_del:
                price_gear_price = decimal.Decimal(price_gear.price)
            else:
                return self.response_json_error("NoGear", "对不起，价格档位已失效")
            # single_lottery_integral = 0.
        module_info_ex.price_gear_id = price_gear_id
        module_info_ex.single_lottery_price = price_gear_price
        if module_info_ex.price_gear_id > 0 and module_info_ex.price_gear_id != price_gear_id:
            module_info_ex.price_gear_modify_date = now_time
        module_info_ex.continuous_lottery_times = continuous_lottery_times
        module_info_ex.single_lottery_integral = single_lottery_integral
        module_info_ex.continuous_lottery_integral = continuous_lottery_integral
        module_info_ex.continuous_lottery_integral_times = continuous_lottery_integral_times
        module_info_ex.is_limit_lottery_times = is_limit_lottery_times
        module_info_ex.single_lottery_limit = single_lottery_limit
        module_info_ex.continuous_lottery_limit = continuous_lottery_limit
        module_info_ex.is_open_all_lottery = is_open_all_lottery
        module_info_ex.all_lottery_count = all_lottery_count
        module_info_ex.is_no_repeat_prize = is_no_repeat_prize
        module_info_ex.is_automatic_buy_back = is_automatic_buy_back
        module_info_ex.automatic_buy_back_days = automatic_buy_back_days
        module_info_ex.is_surplus = is_surplus
        module_info_ex.is_chance = is_chance
        module_info_ex.is_notice = is_notice
        module_info_ex.start_date = start_date
        module_info_ex.end_date = end_date
        module_info_ex.modify_date = now_time

        if is_add:
            module_info_ex.create_date = now_time
            module_info_ex.id = module_info_ex_model.add_entity(module_info_ex)
            # module_info_ex.module_id = module_info_ex.id
            #增加行为映射数据
            self.add_orm_list(act_id, module_info_ex.id)
            # 记录日志
            self.create_operation_log(OperationType.add.value, module_info_ex.__str__(), "MachineHandler", None, self.json_dumps(module_info_ex.__dict__))
        else:
            module_info_ex_model.update_entity(module_info_ex)
            self.create_operation_log(OperationType.update.value, module_info_ex.__str__(), "MachineHandler", self.json_dumps(old_module_info_ex.__dict__), self.json_dumps(module_info_ex.__dict__))

        # 删除依赖建
        business_base_model = BusinessBaseModel(context=self)
        if module_id > 0:
            module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module(module_id))
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module_list(act_id))

        return self.response_json_success(module_info_ex.id)

    def add_orm_list(self, act_id, module_id):
        """
        @description: 添加数据库orm记录
        @param act_id: 活动id
        @param module_id：机台id
        @return {*}
        @last_editors: HuangJingCan
        """
        stat_orm_model = StatOrmModel(context=self)
        now_time = self.get_now_datetime()
        add_stat_orm_list = []
        key_name_module_str = "_" + str(module_id)
        stat_orm_list = stat_orm_model.get_list("group_name='参与情况' and act_id=0 and module_id=0 and is_show=1")
        for stat_orm in stat_orm_list:
            stat_orm.id = 0
            stat_orm.act_id = act_id
            stat_orm.module_id = module_id
            stat_orm.key_name += key_name_module_str
            stat_orm.create_date = now_time
            add_stat_orm_list.append(stat_orm)
        stat_orm_model.add_list(add_stat_orm_list)

    def del_orm_list(self, act_id, module_id):
        """
        @description: 删除数据库orm记录
        @param act_id: 活动id
        @param module_id：机台id
        @return {*}
        @last_editors: HuangJingCan
        """
        stat_orm_model = StatOrmModel(context=self)
        stat_orm_model.del_entity("group_name='参与情况' and act_id=%s and module_id=%s and is_show=1", params=[act_id, module_id])


class MachineListHandler(ClientBaseHandler):
    """
    :description: 机台列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取机台列表
        :param app_id
        :param act_id：活动id
        :param page_index：页索引
        :param page_size：页大小
        :param price_gear_id: 价格挡位id
        :param is_release: 发布状态
        :param ip_id: ip_id
        :return: list
        :last_editors: HuangJingCan
        """
        app_id = self.get_app_id()
        act_id = self.get_param_int("act_id")
        page_index = self.get_param_int("page_index")
        page_size = self.get_param_int("page_size", 10)
        price_gear_id = self.get_param_int("price_gear_id")
        is_release = self.get_param_int("is_release", -1)
        ip_id = self.get_param_int("ip_id")
        module_name = self.get_param("module_name")

        if act_id <= 0:
            return self.response_json_error_params()

        module_info_ex_model = ActModuleExModel(context=self)
        business_base_model = BusinessBaseModel(context=self)
        dependency_key = business_base_model.get_cache_key_act_module_list(act_id)

        params = [act_id]
        condition = ConditionWhere()
        condition.add_condition("act_id=%s and is_del=0")
        if price_gear_id > 0:
            condition.add_condition("price_gear_id=%s")
            params.append(price_gear_id)
        if is_release > -1:
            condition.add_condition("is_release=%s")
            params.append(is_release)
        if ip_id > 0:
            condition.add_condition("ip_id=%s")
            params.append(ip_id)
        if module_name != "":
            condition.add_condition("module_name like %s")
            module_name = f"%{module_name}%"
            params.append(module_name)

        page_dict_list, total = module_info_ex_model.get_cache_dict_page_list("*", page_index, page_size, condition.to_string(), "", "sort_index desc", params, dependency_key)

        if page_dict_list:
            #获取皮肤表
            # skin_info_list = SkinInfoModel(context=self).get_list("app_id=%s", params=[app_id])
            for item in page_dict_list:
                # skin_info = [skin_info for skin_info in skin_info_list if skin_info.id == item["skin_id"]]
                # if skin_info:
                #     item["server_json"] = self.json_loads(skin_info[0].server_json)
                if item["price_gear_modify_date"] == "1900-01-01 00:00:00":
                    item["price_gear_modify_date"] = ""
                if item["start_date"] == "1900-01-01 00:00:00":
                    item["start_date"] = ""
                if item["end_date"] == "1900-01-01 00:00:00":
                    item["end_date"] = ""
                item["online_url"] = self.get_online_url(act_id, app_id) + "," + str(item["ip_id"]) + "," + str(item["id"])

        page_info = PageInfo(page_index, page_size, total, page_dict_list)

        return self.response_json_success(page_info)


class MachineReleaseHandler(ClientBaseHandler):
    """
    :description: 机台上下架
    """
    @filter_check_params("module_id,is_release")
    def get_async(self):
        """
        :description: 机台上下架
        :param module_id：机台id
        :param is_release：是否发布（0下架1上架）
        :return: 
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")
        is_release = self.get_param_int("is_release")
        now_date = TimeHelper.get_now_datetime()

        if module_id <= 0:
            return self.response_json_error_params()

        business_base_model = BusinessBaseModel(context=self)
        module_info_ex_model = ActModuleExModel(context=self)

        module_info = module_info_ex_model.get_cache_dict_by_id(module_id, business_base_model.get_cache_key_act_module(module_id))
        # if module_info and is_release == 1 and module_info["end_date"] != "1900-01-01 00:00:00" and now_date > TimeHelper.format_time_to_datetime(module_info["end_date"]):
        #     return self.response_json_error("ErrorTime", "对不起，机台自动下架时间必须大于当前时间")

        module_info_ex_model.update_table("is_release=%s", "id=%s", [is_release, module_id])

        # 上架机台时更新机台奖品缓存
        if is_release == 1:
            self.sync_prize_surplus(module_id)

        #删除缓存
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module(module_id))
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module_list(module_info['act_id']))
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_module_id(module_id))
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_prize_list_act_id(module_info['act_id']))

        return self.response_json_success()

    def sync_prize_surplus(self, module_id):
        """
        :description: 同步奖品库存到redi
        :param module_id:机台id
        :return: 
        :last_editors: HuangJingCan
        """
        business_base_model = BusinessBaseModel()
        redis_init = SevenHelper.redis_init()
        hash_name = business_base_model.get_cache_key_act_prize_surplus_list(module_id)
        redis_init.delete(hash_name)

        act_prize_model = ActPrizeExModel()
        act_prize_list = act_prize_model.get_list(f"module_id={module_id} and is_del=0")
        for item in act_prize_list:
            redis_init.hset(hash_name, str(item.id), item.surplus)


class MachineDelHandler(ClientBaseHandler):
    """
    :description: 删除机台
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description: 删除机台
        :param module_id：机台id
        :return: response_json_success
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id")

        act_prize_model = ActPrizeModel(context=self)
        act_prize_ex_model = ActPrizeExModel(context=self)
        module_info_ex_model = ActModuleExModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        module_info = module_info_ex_model.get_cache_dict_by_id(module_id, business_base_model.get_cache_key_act_module(module_id))
        if not module_info:
            return self.response_json_error_params()
        act_id = module_info['act_id']

        act_prize_model.update_table("is_del=1", "module_id=%s", [module_id])
        act_prize_ex_model.update_table("is_del=1", "module_id=%s", [module_id])

        module_info_ex_model.update_table("is_del=1", "id=%s", [module_id])

        #删除行为映射数据
        MachineHandler(application=self.application, request=self.request).del_orm_list(act_id, module_id)

        self.create_operation_log(OperationType.delete.value, "act_module_ex_tb", "MachineHandler", None, module_id)

        #删除缓存
        business_base_model = BusinessBaseModel(context=self)
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module(module_id))
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module_list(act_id))

        return self.response_json_success()


class UpdateMachinePriceHandler(ClientBaseHandler):
    """
    :description: 更新机台价格
    """
    @filter_check_params("act_id,price_gear_id")
    def get_async(self):
        """
        :description: 更新价格档位关联的机台价格
        :param act_id：活动id
        :param price_gear_id：价格档位id
        :return: response_json_success
        :last_editors: HuangJingCan
        """
        act_id = self.get_param_int("act_id")
        price_gear_id = self.get_param_int("price_gear_id")

        price_gear_model = PriceGearModel(context=self)
        price_gear_dict = price_gear_model.get_dict_by_id(price_gear_id)
        if not price_gear_dict:
            return self.response_json_error("NoExist", "对不起,价格档位不存在")

        module_info_ex_model = ActModuleExModel(context=self)
        module_info_ex_model.update_table("single_lottery_price=%s", f"price_gear_id={price_gear_id}", params=[decimal.Decimal(price_gear_dict["price"])])

        #删除缓存
        business_base_model = BusinessBaseModel(context=self)
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module_list(act_id))

        return self.response_json_success()


class MachineCopyHandler(ClientBaseHandler):
    """
    :description: 复制机台
    """
    @filter_check_params("module_id")
    def get_async(self):
        """
        :description: 复制机台
        :param module_id：机台id
        :return: response_json_success()
        :last_editors: HuangJingCan
        """
        module_id = self.get_param_int("module_id", 0)
        now_time = self.get_now_datetime()

        module_info_ex_model = ActModuleExModel(context=self)
        act_prize_model = ActPrizeModel(context=self)
        act_prize_ex_model = ActPrizeExModel(context=self)
        act_prize_senior_config_model = ActPrizeSeniorConfigModel(context=self)

        # 获取旧数据，并初始化库存和创建时间
        old_module_info = module_info_ex_model.get_entity_by_id(module_id)
        if not old_module_info:
            return self.response_json_error_params()

        old_module_info.id = 0
        old_module_info.module_name += "_Copy"
        old_module_info.is_release = 0
        old_module_info.is_automatic_buy_back = 0
        old_module_info.automatic_buy_back_days = 0
        old_module_info.modify_date = now_time
        old_module_info.create_date = now_time

        # 获取奖品
        old_prize_ex_list = act_prize_ex_model.get_list("module_id=%s and is_del=0", params=module_id)
        old_prize_list = act_prize_model.get_list("module_id=%s and is_del=0", params=module_id)

        old_prize_ex_dict_list = {}
        for old_prize_ex in old_prize_ex_list:
            old_prize_ex.surplus = old_prize_ex.prize_total
            old_prize_ex.hand_out = 0
            old_prize_ex.is_wait_give = 0
            old_prize_ex.modify_date = now_time
            old_prize_ex.create_date = now_time
            if old_prize_ex.prize_type == 5:
                old_prize_ex.sale_status = 0
            old_prize_ex_dict_list[old_prize_ex.id] = old_prize_ex

        for old_prize in old_prize_list:
            old_prize_ex = old_prize_ex_dict_list[old_prize.id]
            old_prize.modify_date = now_time
            old_prize.create_date = now_time

        new_module_id = module_info_ex_model.add_entity(old_module_info)
        for old_prize in old_prize_list:
            old_prize_ex = old_prize_ex_dict_list[old_prize.id]
            old_prize_copy = deepcopy(old_prize)
            old_prize_copy.id = 0
            old_prize_copy.module_id = new_module_id
            old_prize_ex.id = act_prize_model.add_entity(old_prize_copy)
            # 插入扩展表
            old_prize_ex.module_id = new_module_id
            act_prize_ex_model.add_entity(old_prize_ex)

            # 插入强制概率
            if old_prize_ex.is_senior_ability > 0:
                senior_ability_config = self.json_loads(old_prize_ex.senior_ability_config)
                surplus_lock_count = 0
                must_surplus_count = 0
                for config in senior_ability_config:
                    if config['type_id'] == 1:
                        surplus_lock_count = config['lock_count']
                    elif config['type_id'] == 2:
                        must_surplus_count = config['lock_count']

                act_prize_senior_config = ActPrizeSeniorConfig()
                act_prize_senior_config.prize_id = old_prize_ex.id
                act_prize_senior_config.app_id = old_module_info.app_id
                act_prize_senior_config.act_id = old_module_info.act_id
                act_prize_senior_config.module_id = new_module_id
                act_prize_senior_config.must_surplus_count = must_surplus_count
                act_prize_senior_config.is_lock = 0
                act_prize_senior_config.surplus_lock_count = surplus_lock_count
                act_prize_senior_config.modify_date = now_time
                act_prize_senior_config_model.add_entity(act_prize_senior_config)

        #删除缓存
        business_base_model = BusinessBaseModel(context=self)
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module(module_id))
        module_info_ex_model.delete_dependency_key(business_base_model.get_cache_key_act_module_list(old_module_info.act_id))

        return self.response_json_success()