# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-26 17:51:04
:LastEditTime: 2022-02-17 10:43:54
:LastEditors: HuangJingCan
:Description: 抽奖
"""
import random
from urllib import request
from seven_cloudapp_frame.handlers.frame_base import *

from seven_cloudapp_frame.models.stat_base_model import StatBaseModel
from seven_cloudapp_frame.models.asset_base_model import AssetBaseModel
from seven_cloudapp_frame.models.frame_base_model import FrameBaseModel

from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *

from seven_cloudapp_ndjyfs.models.enum import *
from seven_cloudapp_ndjyfs.models.business_base_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_info_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_module_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.prize.prize_roster_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.act.act_prize_senior_config_model import *
from seven_cloudapp_ndjyfs.models.db_models.user.user_info_ex_model import *
from seven_cloudapp_ndjyfs.models.db_models.lottery.lottery_log_model import *


class ALLLotteryHandler(ClientBaseHandler):
    """
    :description: 全收抽奖
    """
    @filter_check_params("lottery_permit")
    def get_async(self):
        """
        :description: 抽奖
        :param login_token:登录令牌
        :param act_id:活动id
        :param module_id:机台id
        :param asset_type：抽奖类型（2积分，3价格档位次数）
        :return: 抽奖
        :last_editors: HuangJingCan
        """
        lottery_permit = self.get_param("lottery_permit")
        total_surplus = self.get_param_int("total_surplus")
        open_id = self.get_open_id()

        # 根据抽奖取出redis数据
        hash_name = f"lottery_permit_list:openid_{open_id}"
        redis_init = SevenHelper.redis_init()
        lottery_data = redis_init.hget(hash_name, lottery_permit)
        if lottery_data:
            lottery_data = SevenHelper.json_loads(lottery_data)
            redis_init.hdel(hash_name, lottery_permit)
        else:
            return self.response_json_error("ErroPermit", "对不起，抽奖失败，请重试")
        if not lottery_data:
            return self.response_json_error("ErroLotteryData", "对不起，抽奖失败，请重试")
        self.logging_link_info("【抽奖许可信息】" + str(lottery_data))
        if open_id != lottery_data["open_id"]:
            return self.response_json_error("ErroOpenId", "对不起，抽奖失败，请重试")

        app_id = lottery_data["app_id"]
        act_id = lottery_data["act_id"]
        user_id = lottery_data["user_id"]
        user_info_id = lottery_data["user_info_id"]
        user_nick = lottery_data["user_nick"]
        asset_type = lottery_data["asset_type"]
        module_id = lottery_data["module_id"]
        act_is_open_buy_back = lottery_data["act_is_open_buy_back"]

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        user_info_ex_model = UserInfoExModel(db_transaction=db_transaction, context=self)
        act_prize_model = ActPrizeExModel(db_transaction=db_transaction, context=self)
        machine_info_model = ActModuleExModel(db_transaction=db_transaction, context=self)
        act_prize_senior_config_model = ActPrizeSeniorConfigModel(db_transaction=db_transaction, context=self)
        asset_base_model = AssetBaseModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        # #请求太频繁限制
        # if self.check_continue_request("Lottery_Post", app_id, open_id, 1000) == False:
        #     return self.response_json_error("HintMessage", "哎呀~当前操作人数过多")
        # if self.check_continue_request("All_Lottery_Post", app_id, module_id, 500) == False:
        #     return self.response_json_error("HintMessage2", "哎呀~当前操作人数过多")

        # # 判断用户资质
        # user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        # if not user_info:
        #     return self.response_json_error("NoUser", "对不起，用户不存在")
        # if user_info.user_state == 1:
        #     return self.response_json_error("UserState", "对不起，你是黑名单用户,无法抽扭蛋")
        # if user_info.login_token != login_token:
        #     return self.response_json_error("ErrorToken", "对不起，已在另一台设备登录,无法抽扭蛋")
        # if not user_info.user_nick:
        #     return self.response_json_error("ErrorUserNick", "对不起，用户未授权")
        # user_id = user_info.user_id
        # user_nick = user_info.user_nick

        # # 判断活动信息
        # dependency_key = business_base_model.get_cache_key_act_info(act_id)
        # act_info = act_info_model.get_cache_entity_by_id(act_id, dependency_key=dependency_key, cache_expire=1800)
        # act_info_ex = act_info_ex_model.get_cache_entity_by_id(act_id, dependency_key=dependency_key, cache_expire=1800)
        # if not act_info or not act_info_ex or act_info.is_release == 0 or act_info.is_del == 1:
        #     return self.response_json_error("NoAct", "对不起，活动不存在")
        # if now_date < act_info.start_date:
        #     return self.response_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        # if now_date > act_info.end_date:
        #     return self.response_json_error("NoAct", "活动已结束")

        #获取机台信息
        machine_dependency_key = business_base_model.get_cache_key_act_module(module_id)
        machine_info = machine_info_model.get_cache_entity_by_id(module_id, dependency_key=machine_dependency_key, cache_expire=1800)
        if not machine_info or machine_info.is_release == 0:
            return self.response_json_error("NoMachine", "对不起，机台不存在")
        # if machine_info.start_date == "1900-01-01 00:00:00":
        #     sale_date = now_date
        # else:
        #     sale_date = str(machine_info.start_date)
        # sale_date = TimeHelper.format_time_to_datetime(sale_date)
        # if TimeHelper.format_time_to_datetime(now_date) < sale_date:
        #     china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
        #     return self.response_json_error("NoAct", "机台将在" + china_sale_date + "开售,敬请期待~")
        # if machine_info.end_date != "1900-01-01 00:00:00" and now_date > machine_info.end_date:
        #     return self.response_json_error("NoAct", "机台已下架")
        # if not machine_info.is_open_all_lottery:
        #     return self.response_json_error("NoOpenAllLottery", "对不起，全收未开启")

        # 上限200件全收
        if machine_info.all_lottery_count == 0:
            machine_info.all_lottery_count = 200

        key_act_prize_list = business_base_model.get_cache_key_act_prize_list_module_id(module_id)
        prize_sum_dict = act_prize_model.get_cache_dict("module_id=%s and is_del=0 and is_release=1 and yfs_type=1 and surplus>0", field="CAST(SUM(surplus) AS SIGNED) AS prize_surplus_sum", params=[module_id], dependency_key=key_act_prize_list)
        prize_surplus_sum = prize_sum_dict["prize_surplus_sum"] if prize_sum_dict["prize_surplus_sum"] else 0  # 奖品库存剩余总数量
        if prize_surplus_sum and prize_surplus_sum > machine_info.all_lottery_count:
            return self.response_json_error("RulesChange", f"本奖池奖品剩余{machine_info.all_lottery_count}件时，才可全收")

        #抽奖次数
        lottery_count = int(prize_surplus_sum)
        if lottery_count != total_surplus:
            return self.response_json_error("RefreshSurplus", f"对不起，请刷新库存")

        #开启高级功能的奖品数量
        hash_name = business_base_model.get_cache_key_act_prize_surplus_list(module_id)
        redis_init = SevenHelper.redis_init()
        hash_data_list = redis_init.hgetall(hash_name)
        if not hash_data_list:
            #由于调试过程中需要多次删除缓存查bug，本句保留，线上环境可考虑删除
            self.sync_prize_surplus(redis_init, business_base_model, module_id)
            hash_data_list = redis_init.hgetall(hash_name)
        if not hash_data_list:
            return self.response_json_error("NoPrize_01", "对不起，奖品库存不足")

        expire_time = 2 * 365 * 24 * 3600
        redis_init.expire(hash_name, expire_time)  #hash保留两年

        #价格档位
        store_pay_price = 0  #累计支付金额（任务使用）
        price_gear_id = machine_info.price_gear_id
        #用户剩余资产
        user_asset_value = 0
        asset_object_id = ""
        asset_value = 0
        lottery_type_unit = "积分"
        user_asset_dict_list = asset_base_model.get_user_asset_list(app_id, act_id, user_id, asset_type)
        if asset_type == 3:
            asset_object_id = str(price_gear_id)
            lottery_type_unit = "次数"
            asset_value = lottery_count
            store_pay_price = lottery_count * float(machine_info.single_lottery_price)
            for user_asset_dict in user_asset_dict_list:
                if user_asset_dict["asset_object_id"] == asset_object_id:
                    user_asset_value = user_asset_dict["asset_value"]
                    break
        elif asset_type == 2:
            asset_value = lottery_count * machine_info.single_lottery_integral
            user_asset_value = user_asset_dict_list[0]["asset_value"] if len(user_asset_dict_list) else 0

        if user_asset_value < asset_value:
            return self.response_json_error("NoLotteryCount", f"对不起，{lottery_type_unit}不足")

        # 获取机台奖品
        act_prize_list = act_prize_model.get_cache_dict_list("module_id=%s and is_del=0 and is_release=1 and yfs_type=1 and surplus>0", order_by="sort_index desc", params=[module_id], dependency_key=key_act_prize_list, cache_expire=1800)

        #可抽奖品数量
        lottery_prize_count = 0
        #本次抽取奖品列表
        lottery_prize_list = []

        for act_prize in act_prize_list:
            # 全收时，0概率的也出奖
            lottery_prize_count += int(act_prize["surplus"])
            # 抽奖
            for i in range(int(act_prize["surplus"])):
                lottery_prize_list.append(act_prize)
        if len(act_prize_list) == 0 or lottery_prize_count < lottery_count:
            return self.response_json_error("NoLotteryCount_1", "对不起，奖品库存不足")

        if len(lottery_prize_list) != lottery_count:
            return self.response_json_error("NoLotteryCount_4", "对不起，奖品库存不足")

        # 乱序排列中奖顺序
        lottery_prize_list = self.random_prize_sort(lottery_prize_list)

        # # 判断是否抽空机台，并且是否存在最终赏，然后发放最终赏
        # is_end = 0
        # if lottery_prize_count == lottery_count:
        #     is_end = 1
        #     act_prize_End = act_prize_model.get_cache_dict("module_id=%s and is_del=0 and is_release=1 and surplus>0 and yfs_key_name='End'", order_by="sort_index desc", params=[module_id], dependency_key=key_act_prize_list)
        #     if act_prize_End:
        #         lottery_prize_list = [act_prize_End] + lottery_prize_list

        #扣库存，没库存则回补
        success_update_surplus_list = []
        update_surplus_result = True
        for act_prize in act_prize_list:
            now_surplus = redis_init.hincrby(hash_name, str(act_prize["id"]), -act_prize["surplus"])
            if now_surplus < 0:
                redis_init.hincrby(hash_name, str(act_prize["id"]), act_prize["surplus"])
                update_surplus_result = False
                break
            else:
                success_update_surplus_list.append(str(act_prize["id"]))
        if update_surplus_result == False:
            for item in success_update_surplus_list:
                redis_init.hincrby(hash_name, item, act_prize["surplus"])
            return self.response_json_error("NoSurplus_5", "对不起，奖品库存不足")
        try:
            #开始事务
            db_transaction.begin_transaction()
            # 扣除资产
            invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, module_id, user_id, open_id, user_nick, asset_type, -asset_value, asset_object_id, 4, "", "", f"【{machine_info.module_name}】全收")
            if invoke_result_data.success == False:
                self.logging_link_error("FailUpdateAsset:" + str(invoke_result_data.__dict__))
                return self.response_json_error("ErrorAsset", "对不起，抽奖失败")

            #更新用户信息
            user_update = "all_lottery_count=all_lottery_count+1"
            user_params = []

            if asset_type == 3:
                user_update += ",store_pay_price=store_pay_price+%s"
                user_params.append(store_pay_price)

            user_params.append(user_info_id)

            user_info_ex_model.update_table(user_update, f"id=%s", user_params)

            #结束事务
            db_transaction.commit_transaction()
            # 删除高级功能缓存
            key_senior_config = business_base_model.get_cache_key_act_prize_senior_config_list(act_id, module_id)
            act_prize_senior_config_model.delete_dependency_key(key_senior_config)

            redis_init = SevenHelper.redis_init()
            prize_roster_list = []

            for act_prize in lottery_prize_list:
                #录入用户奖品
                prize_roster = {}
                prize_roster["app_id"] = app_id
                prize_roster["act_id"] = act_id
                prize_roster["open_id"] = open_id
                prize_roster["user_id"] = user_id
                prize_roster["user_nick"] = user_nick
                prize_roster["price_gear_id"] = price_gear_id
                prize_roster["ip_id"] = act_prize["ip_id"]
                prize_roster["module_id"] = act_prize["module_id"]
                prize_roster["module_name"] = machine_info.module_name
                prize_roster["module_type"] = machine_info.module_type
                prize_roster["module_price"] = machine_info.single_lottery_integral if asset_type == 2 else machine_info.single_lottery_price
                prize_roster["asset_type"] = asset_type
                prize_roster["act_is_open_buy_back"] = act_is_open_buy_back
                prize_roster["is_automatic_buy_back"] = machine_info.is_automatic_buy_back
                prize_roster["automatic_buy_back_days"] = machine_info.automatic_buy_back_days
                prize_roster["request_code"] = self.request_code
                prize_roster["is_end"] = 1
                prize_roster["source_type"] = 1
                prize_roster["act_prize"] = act_prize
                prize_roster_list.append(prize_roster)

                redis_init.hincrby(f"prize_roster_count_list:{act_id}", f"openid_{open_id}_prizeid_{act_prize['id']}", 1)
            redis_init.rpush(f"lottery_prize_roster_list:{str(module_id % 10)}", SevenHelper.json_dumps(prize_roster_list))
        except Exception as ex:
            #回滚事务
            if db_transaction.is_transaction == True:
                db_transaction.rollback_transaction()
            self.logging_link_error("ALLLotteryHandler:" + str(len(lottery_prize_list)) + ":" + traceback.format_exc())
            return self.response_json_error("NoLottery", "对不起，全收失败")

        result = {}
        result["prize_list"] = lottery_prize_list

        return self.response_json_success(result)

    def random_prize_sort(self, lottery_prize_list):
        """
        :description: 乱序排列中奖顺序
        :param lottery_prize_list：本次抽取奖品列表
        :return: 
        :last_editors: HuangJingCan
        """
        result_list = []
        lottery_prize_len = len(lottery_prize_list)

        for i in range(lottery_prize_len):
            index = random.randint(1, len(lottery_prize_list)) - 1
            result_list.append(lottery_prize_list.pop(index))

        return result_list

    def sync_prize_surplus(self, redis_init, business_base_model, module_id):
        """
        :description: 同步奖品库存到redis，注意：新产品都是后台直接同步，不需要调用当前方法，只有旧产品，为了兼容才需要在第一次同步库存
        :param redis_init:redis_init
        :param module_id:机台id
        :return: 
        :last_editors: HuangJingCan
        """
        hash_name = business_base_model.get_cache_key_act_prize_surplus_list(module_id)
        act_prize_model = ActPrizeExModel()
        act_prize_list = act_prize_model.get_list(f"module_id={module_id} and is_del=0")
        for item in act_prize_list:
            redis_init.hincrby(hash_name, str(item.id), item.surplus)


class LotteryHandler(ClientBaseHandler):
    """
    :description: 抽奖
    """
    @filter_check_params("lottery_permit")
    def get_async(self):
        """
        :description: 抽奖
        :param login_token:登录令牌
        :param act_id:活动id
        :param module_id: 机台id
        :param lottery_type：抽奖模式（1单抽2连抽）
        :param asset_type：抽奖类型（2积分，3价格档位次数）
        :return: 抽奖
        :last_editors: HuangJingCan
        """
        lottery_permit = self.get_param("lottery_permit")
        open_id = self.get_open_id()

        # 根据抽奖取出redis数据
        hash_name = f"lottery_permit_list:openid_{open_id}"
        redis_init = SevenHelper.redis_init()
        lottery_data = redis_init.hget(hash_name, lottery_permit)
        if lottery_data:
            lottery_data = SevenHelper.json_loads(lottery_data)
            redis_init.hdel(hash_name, lottery_permit)
        else:
            return self.response_json_error("ErroPermit", "对不起，抽奖失败，请重试")
        if not lottery_data:
            return self.response_json_error("ErroLotteryData", "对不起，抽奖失败，请重试")
        self.logging_link_info("【抽奖许可信息】" + str(lottery_data))
        if open_id != lottery_data["open_id"]:
            return self.response_json_error("ErroOpenId", "对不起，抽奖失败，请重试")

        app_id = lottery_data["app_id"]
        act_id = lottery_data["act_id"]
        user_id = lottery_data["user_id"]
        user_info_id = lottery_data["user_info_id"]
        user_nick = lottery_data["user_nick"]
        asset_type = lottery_data["asset_type"]
        module_id = lottery_data["module_id"]
        lottery_type = lottery_data["lottery_type"]
        act_is_open_buy_back = lottery_data["act_is_open_buy_back"]

        #请求太频繁限制
        if self.check_continue_request("Lottery_Post", app_id, open_id) == False:
            return self.response_json_error("HintMessage", "哎呀~当前操作人数过多")

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        user_info_ex_model = UserInfoExModel(db_transaction=db_transaction, context=self)
        act_prize_model = ActPrizeExModel(db_transaction=db_transaction, context=self)
        machine_info_model = ActModuleExModel(db_transaction=db_transaction, context=self)
        act_prize_senior_config_model = ActPrizeSeniorConfigModel(db_transaction=db_transaction, context=self)
        asset_base_model = AssetBaseModel(context=self)
        frame_base_model = FrameBaseModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        # #请求太频繁限制
        # if self.check_continue_request("Lottery_Post", app_id, open_id) == False:
        #     return self.response_json_error("HintMessage", "哎呀~当前操作人数过多")

        # # 判断用户资质
        # user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        # if not user_info:
        #     return self.response_json_error("NoUser", "对不起，用户不存在")
        # if user_info.user_state == 1:
        #     return self.response_json_error("UserState", "对不起，你是黑名单用户,无法抽扭蛋")
        # if user_info.login_token != login_token:
        #     return self.response_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽扭蛋")
        # if not user_info.user_nick:
        #     return self.response_json_error("ErrorUserNick", "对不起，用户未授权")
        # user_id = user_info.user_id
        # user_nick = user_info.user_nick
        # # invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, module_id, user_id, open_id, user_nick, asset_type, 1000, 3, 3, "", "", f"手动添加")
        # # return

        # # 判断活动信息
        # key_act_info = business_base_model.get_cache_key_act_info(act_id)
        # act_info = act_info_model.get_cache_entity_by_id(act_id, dependency_key=key_act_info, cache_expire=1800)
        # act_info_ex = act_info_ex_model.get_cache_entity_by_id(act_id, dependency_key=key_act_info, cache_expire=1800)
        # if not act_info or not act_info_ex or act_info.is_release == 0 or act_info.is_del == 1:
        #     return self.response_json_error("NoAct", "对不起，活动不存在")
        # if now_date < act_info.start_date:
        #     return self.response_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        # if now_date > act_info.end_date:
        #     return self.response_json_error("NoAct", "活动已结束")

        # #获取机台信息
        key_act_module = business_base_model.get_cache_key_act_module(module_id)
        machine_info = machine_info_model.get_cache_entity_by_id(module_id, dependency_key=key_act_module, cache_expire=1800)
        if not machine_info or machine_info.is_release == 0:
            return self.response_json_error("NoMachine", "对不起，机台不存在")
        # if machine_info.start_date == "1900-01-01 00:00:00":
        #     sale_date = now_date
        # else:
        #     sale_date = str(machine_info.start_date)
        # sale_date = TimeHelper.format_time_to_datetime(sale_date)
        # if TimeHelper.format_time_to_datetime(now_date) < sale_date:
        #     china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
        #     return self.response_json_error("NoAct", "机台将在" + china_sale_date + "开售,敬请期待~")
        # if machine_info.end_date != "1900-01-01 00:00:00" and now_date > machine_info.end_date:
        #     return self.response_json_error("NoAct", "机台已下架")
        # if (asset_type != 2 and machine_info.module_type == 2) or (asset_type != 3 and machine_info.module_type == 1):
        #     return self.response_json_error("ErrorType", "对不起，抽奖失败")

        #开启高级功能的奖品数量
        hash_name = business_base_model.get_cache_key_act_prize_surplus_list(module_id)
        hash_data_list = redis_init.hgetall(hash_name)
        if not hash_data_list:
            #由于调试过程中需要多次删除缓存查bug，本句保留，线上环境可考虑删除
            self.sync_prize_surplus(redis_init, business_base_model, module_id)
            hash_data_list = redis_init.hgetall(hash_name)
        if not hash_data_list:
            return self.response_json_error("NoPrize_01", "对不起，奖品库存不足")

        expire_time = 2 * 365 * 24 * 3600
        redis_init.expire(hash_name, expire_time)  #hash保留两年
        # 获取机台奖品
        key_act_prize_list = business_base_model.get_cache_key_act_prize_list_module_id(module_id)
        act_prize_list = act_prize_model.get_cache_dict_list("module_id=%s and is_del=0 and is_release=1 and yfs_type=1", order_by="sort_index desc", params=[module_id], dependency_key=key_act_prize_list, cache_expire=1800)

        # 获取机台总奖品剩余数量
        totle_surplus_count = 0
        if len(act_prize_list) <= 0:
            return self.response_json_error("NoPrize_02", "对不起，奖品库存不足")
        act_prize_senior_total = 0
        for act_prize in act_prize_list:
            if act_prize["is_senior_ability"] == 1:
                act_prize_senior_total += 1
            if hash_data_list.__contains__(str(act_prize["id"])):
                act_prize["surplus"] = int(hash_data_list[str(act_prize["id"])])
            else:
                act_prize["surplus"] = 0
            totle_surplus_count += act_prize["surplus"]

        #有高级配置需要走分布式锁
        if act_prize_senior_total > 0:
            #redis分布式锁
            queue_name = f"Machine_Queue_{str(module_id)}"
            identifier = SevenHelper.redis_acquire_lock(queue_name)
            if isinstance(identifier, bool):
                return self.response_json_error("UserLimit", "当前人数过多,请稍后再来")

        # 价格档位id
        price_gear_id = machine_info.price_gear_id if asset_type == 3 else 0
        #抽奖次数
        lottery_count = 1
        #使用积分
        use_integral = machine_info.single_lottery_integral
        #全部可抽奖品列表
        all_lottery_prize_list = []
        #可抽奖品数量
        lottery_prize_count = 0
        #剩余库存
        all_surplus = 0
        #本次抽取奖品列表
        lottery_prize_list = []
        if lottery_type == 2:
            lottery_count = machine_info.continuous_lottery_times if asset_type == 3 else (machine_info.continuous_lottery_integral_times if asset_type == 2 else 0)
            use_integral = machine_info.continuous_lottery_integral
        if lottery_count <= 0:
            if act_prize_senior_total > 0:
                SevenHelper.redis_release_lock(queue_name, identifier)
            return self.response_json_error("Error", "对不起，当前机台不能连抽")
        # 获取用户剩余资产
        user_asset_dict_list = []
        user_asset_value = 0  #用户剩余资产
        asset_value = 0  # 需要扣除资产
        asset_object_id = ""  # 资产标识
        user_asset_dict_list = asset_base_model.get_user_asset_list(app_id, act_id, user_id, asset_type)
        #次数抽奖
        if asset_type == 3:
            asset_object_id = price_gear_id
            asset_value = lottery_count
            for user_asset_dict in user_asset_dict_list:
                if int(user_asset_dict["asset_object_id"]) == asset_object_id:
                    user_asset_value = user_asset_dict["asset_value"]
                    break
            if user_asset_value < asset_value:
                if act_prize_senior_total > 0:
                    SevenHelper.redis_release_lock(queue_name, identifier)
                return self.response_json_error("NoLotteryCount", "对不起，次数不足")
        #积分机台
        elif asset_type == 2:
            asset_object_id = ""
            asset_value = use_integral
            if len(user_asset_dict_list):
                user_asset_value = user_asset_dict_list[0]["asset_value"]
            if user_asset_value < asset_value:
                if act_prize_senior_total > 0:
                    SevenHelper.redis_release_lock(queue_name, identifier)
                return self.response_json_error("NoLotteryCount", "对不起，积分不足")

        #过滤奖品
        for act_prize in act_prize_list:
            all_surplus += act_prize["surplus"] if act_prize["surplus"] > 0 else 0
            if act_prize["surplus"] <= 0 or act_prize["probability"] <= 0:
                continue
            if machine_info.is_no_repeat_prize == 0:
                lottery_prize_count += int(act_prize["surplus"])
            else:
                lottery_prize_count += 1
            all_lottery_prize_list.append(act_prize)

        #判断库存
        if lottery_prize_count < lottery_count:
            if act_prize_senior_total > 0:
                SevenHelper.redis_release_lock(queue_name, identifier)
            return self.response_json_error("NoSurplus_1", "对不起，奖品库存不足")

        #获取活动奖品高级配置列表
        key_senior_config = business_base_model.get_cache_key_act_prize_senior_config_list(act_id, module_id)
        act_prize_senior_config_list = act_prize_senior_config_model.get_cache_dict_list("act_id=%s and module_id=%s", params=[act_id, module_id], dependency_key=key_senior_config, cache_expire=1800)
        #抽奖
        for i in range(lottery_count):
            #当前可抽取的奖品列表
            cur_lottery_prize_list = self.prize_senior_limit(all_lottery_prize_list, act_prize_senior_config_list, lottery_prize_list, open_id, machine_info.__dict__, totle_surplus_count)
            if not cur_lottery_prize_list:
                if act_prize_senior_total > 0:
                    SevenHelper.redis_release_lock(queue_name, identifier)
                return self.response_json_error("NoSurplus_2", "对不起，奖品库存不足")
            #权重抽奖
            lottery_prize = frame_base_model.lottery_algorithm_probability(cur_lottery_prize_list)
            if not lottery_prize:
                if act_prize_senior_total > 0:
                    SevenHelper.redis_release_lock(queue_name, identifier)
                return self.response_json_error("NoSurplus_3", "对不起，奖品库存不足")
            #转换为对象
            # lottery_prize = SevenHelper.auto_mapper(ActPrize(), lottery_prize)
            lottery_prize_list.append(lottery_prize)
            #奖品高级功能计数扣除
            act_prize_senior_config_list = self.prize_count_deduct(all_lottery_prize_list, act_prize_senior_config_list, lottery_prize)
            #奖品扣除
            for all_lottery_prize in all_lottery_prize_list:
                if all_lottery_prize["id"] == lottery_prize["id"]:
                    all_lottery_prize["surplus"] -= 1

        if len(lottery_prize_list) != lottery_count:
            if act_prize_senior_total > 0:
                SevenHelper.redis_release_lock(queue_name, identifier)
            return self.response_json_error("NoSurplus_4", "对不起，奖品库存不足")

        #扣库存，没库存则回补
        success_update_surplus_list = []
        update_surplus_result = True
        for act_prize in lottery_prize_list:
            now_surplus = redis_init.hincrby(hash_name, str(act_prize["id"]), -1)
            if now_surplus < 0:
                redis_init.hincrby(hash_name, str(act_prize["id"]), 1)
                update_surplus_result = False
                break
            else:
                success_update_surplus_list.append(str(act_prize["id"]))
        if update_surplus_result == False:
            if act_prize_senior_total > 0:
                SevenHelper.redis_release_lock(queue_name, identifier)
            for item in success_update_surplus_list:
                redis_init.hincrby(hash_name, item, 1)
            return self.response_json_error("NoSurplus_5", "对不起，奖品库存不足")
        try:
            #开始事务
            db_transaction.begin_transaction()
            # 扣除资产
            invoke_result_data = asset_base_model.update_user_asset(app_id, act_id, module_id, user_id, open_id, user_nick, asset_type, -asset_value, asset_object_id, 4, "", "", f"【{machine_info.module_name}】抽奖")
            if invoke_result_data.success == False:
                if act_prize_senior_total > 0:
                    SevenHelper.redis_release_lock(queue_name, identifier)
                self.logging_link_error("FailUpdateAsset:" + str(invoke_result_data.__dict__))
                return self.response_json_error("ErrorAsset", "对不起，抽奖失败")

            #更新用户信息
            user_update = "lottery_sum=lottery_sum+%s"
            user_params = [lottery_count]
            button_num = self.get_button_num(lottery_type, asset_type)
            if button_num == 1:
                user_update += ",integral_single_lottery_count=integral_single_lottery_count+1"
            elif button_num == 2:
                user_update += ",integral_continuous_lottery_count=integral_continuous_lottery_count+1"
            elif button_num == 3:
                user_update += ",price_single_lottery_count=price_single_lottery_count+1,store_pay_price=store_pay_price+%s"
                user_params.append(float(machine_info.single_lottery_price))
            elif button_num == 4:
                user_update += ",price_continuous_lottery_count=price_continuous_lottery_count+1,store_pay_price=store_pay_price+%s"
                user_params.append(float(machine_info.single_lottery_price) * lottery_count)
            # user_params += [act_id, user_id]
            user_params.append(user_info_id)

            user_info_ex_model.update_table(user_update, "id=%s", user_params)

            # 更新缓存中抽奖计数--每日中奖限制功能
            if machine_info.is_limit_lottery_times:
                now_day = SevenHelper.get_now_day_int()
                hash_name = f"lottery_limit_list:moduleid_{module_id}"
                key_lottery_limit = f"openid_{open_id}_day_{now_day}_type_{lottery_type}"
                redis_init.hincrby(hash_name, key_lottery_limit)
                expire_time = 24 * 3600  # 过期时间一天
                redis_init.expire(hash_name, expire_time)

            #更新奖品高级配置计数
            act_prize_senior_config_list_update = []
            for item in act_prize_senior_config_list:
                item = SevenHelper.auto_mapper(ActPrizeSeniorConfig(), item)
                act_prize_senior_config_list_update.append(item)
            act_prize_senior_config_model.update_list(act_prize_senior_config_list_update, "modify_date,surplus_lock_count,is_lock,must_surplus_count")

            #结束事务
            db_transaction.commit_transaction()

            # 删除高级功能缓存
            if len(act_prize_senior_config_list_update):
                key_senior_config = business_base_model.get_cache_key_act_prize_senior_config_list(act_id, module_id)
                act_prize_senior_config_model.delete_dependency_key(key_senior_config)

            prize_roster_list = []
            # 判断是否抽空机台
            is_end = 1 if all_surplus == lottery_count else 0
            # 判断活动回购是否开启
            for act_prize in lottery_prize_list:
                #录入用户奖品
                prize_roster = {}
                prize_roster["app_id"] = app_id
                prize_roster["act_id"] = act_id
                prize_roster["open_id"] = open_id
                prize_roster["user_id"] = user_id
                prize_roster["user_nick"] = user_nick
                prize_roster["price_gear_id"] = price_gear_id
                prize_roster["ip_id"] = act_prize["ip_id"]
                prize_roster["module_id"] = act_prize["module_id"]
                prize_roster["module_name"] = machine_info.module_name
                prize_roster["module_type"] = machine_info.module_type
                prize_roster["module_price"] = machine_info.single_lottery_integral if asset_type == 2 else machine_info.single_lottery_price
                prize_roster["asset_type"] = asset_type
                prize_roster["act_is_open_buy_back"] = act_is_open_buy_back
                prize_roster["is_automatic_buy_back"] = machine_info.is_automatic_buy_back
                prize_roster["automatic_buy_back_days"] = machine_info.automatic_buy_back_days
                prize_roster["request_code"] = self.request_code
                prize_roster["is_end"] = is_end
                prize_roster["source_type"] = 1
                prize_roster["act_prize"] = act_prize
                prize_roster_list.append(prize_roster)

                redis_init.hincrby(f"prize_roster_count_list:{act_id}", f"openid_{open_id}_prizeid_{act_prize['id']}", 1)
            redis_init.rpush(f"lottery_prize_roster_list:{str(module_id % 10)}", SevenHelper.json_dumps(prize_roster_list))
        except Exception as ex:
            #回滚事务
            if db_transaction.is_transaction == True:
                db_transaction.rollback_transaction()
            self.logging_link_error("LotteryHandler:" + SevenHelper.json_dumps(lottery_prize_list) + ":" + traceback.format_exc())
            if act_prize_senior_total > 0:
                SevenHelper.redis_release_lock(queue_name, identifier)
            return self.response_json_error("NoLottery", "对不起，扭蛋失败")
        result = {}
        result["prize_list"] = lottery_prize_list
        result["lottery_type"] = lottery_type
        #解锁
        if act_prize_senior_total > 0:
            SevenHelper.redis_release_lock(queue_name, identifier)

        self.response_json_success(result)

    def get_button_num(self, lottery_type, asset_type):
        """
        :description: 获取每日限制按钮编号：1积分单抽，2积分连抽，3价格档位单抽，4价格档位次数连抽
        :param lottery_type：抽奖模式（1单抽2连抽）
        :param asset_type：抽奖类型（2积分，3价格档位次数）
        :return:button_num
        """
        if lottery_type == 1:
            if asset_type == 2:
                return 1
            if asset_type == 3:
                return 3
        if lottery_type == 2:
            if asset_type == 2:
                return 2
            if asset_type == 3:
                return 4
        return 0

    def prize_senior_limit(self, prize_list, act_prize_senior_config_list, lottery_prize_list, open_id, machine_info_dict, totle_surplus_count):
        """
        :description: 奖品高级功能限制
        :param prize_list:全部可抽奖列表
        :param act_prize_senior_config_list:奖品高级配置列表
        :param lottery_prize_list:已抽中的奖品列表
        :param open_id:用户open_id
        :return: 可抽奖品列表
        :param params:参数
        """
        #必中奖品列表
        must_prize_list = []
        #抽奖奖品列表
        cur_prize_list = []
        prize_roster_model = PrizeRosterExModel(context=self)
        #总概率
        # sum_chance = 0
        for prize in prize_list:
            #判断库存
            if prize["surplus"] <= 0:
                continue
            #奖品是否重复
            if int(machine_info_dict["is_no_repeat_prize"]) == 1:
                lottery_prize = [lottery_prize for lottery_prize in lottery_prize_list if lottery_prize["id"] == prize["id"]]
                if lottery_prize:
                    continue
            is_add = True
            # 优先判断中奖限制
            if prize["is_open_prize_limit"]:
                redis_init = SevenHelper.redis_init()
                hash_name = f"prize_roster_count_list:{prize['act_id']}"
                hash_key = f"openid_{open_id}_prizeid_{prize['id']}"
                lottery_count = redis_init.hget(hash_name, hash_key)
                if lottery_count:
                    lottery_count = int(lottery_count)
                else:
                    key_prize_roster_list = BusinessBaseModel().get_cache_key_prize_roster_list(prize['act_id'])
                    lottery_count = prize_roster_model.get_cache_total("act_id=%s and open_id=%s and prize_id=%s", params=[prize["act_id"], open_id, prize["id"]], dependency_key=key_prize_roster_list)
                    redis_init.hincrby(hash_name, hash_key, lottery_count)
                cur_lottery_prize_list = [lottery_prize for lottery_prize in lottery_prize_list if lottery_prize["id"] == prize["id"]]
                lottery_count += len(cur_lottery_prize_list)
                if lottery_count >= int(prize["prize_limit"]):
                    is_add = False
            is_must = False
            if prize["is_senior_ability"] == 1 and prize["senior_ability_config"] and is_add:
                senior_ability_config_list = SevenHelper.json_loads(prize["senior_ability_config"])
                #遍历高级功能 --
                for senior_ability_config in senior_ability_config_list:
                    if int(senior_ability_config["is_open"]) == 1:
                        if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.奖品锁定.value:
                            # 锁定且未到解锁时机
                            if prize["surplus"] <= senior_ability_config["lock_count"] and senior_ability_config["unlock_count"] < totle_surplus_count - len(lottery_prize_list):
                                is_add = False
                                break
                        if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.强制出奖.value:
                            act_prize_senior_config = [act_prize_senior_config for act_prize_senior_config in act_prize_senior_config_list if act_prize_senior_config["prize_id"] == prize["id"]]
                            if act_prize_senior_config:
                                act_prize_senior_config = act_prize_senior_config[0]
                                if act_prize_senior_config["is_lock"] == 1:
                                    is_add = False
                                    break
                                if act_prize_senior_config["must_surplus_count"] <= 1:
                                    is_must = True
            if is_add == True:
                # sum_chance += float(prize["chance"])
                cur_prize_list.append(prize)
                if is_must == True:
                    must_prize_list.append(prize)
        if len(must_prize_list) > 0:
            cur_prize_list = must_prize_list
        return cur_prize_list

    def prize_count_deduct(self, prize_list, act_prize_senior_config_list, lottery_prize):
        """
        :description: 奖品计数扣除（高级功能）
        :param prize_list:全部可抽奖列表
        :param lottery_prize:已抽中奖品
        :return: 最后奖品高级配置列表
        :param params:参数
        """
        last_act_prize_senior_config_list = []
        for prize in prize_list:
            if prize["is_senior_ability"] == 1 and prize["senior_ability_config"]:
                act_prize_senior_config = [act_prize_senior_config for act_prize_senior_config in act_prize_senior_config_list if act_prize_senior_config["prize_id"] == prize["id"]]
                if act_prize_senior_config:
                    act_prize_senior_config = act_prize_senior_config[0]
                    senior_ability_config_list = SevenHelper.json_loads(prize["senior_ability_config"])
                    #遍历高级功能
                    now_date = self.get_now_datetime()
                    for senior_ability_config in senior_ability_config_list:
                        if int(senior_ability_config["is_open"]) == 1:
                            # if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.奖品锁定.value and act_prize_senior_config["surplus_lock_count"] > 0:
                            #     act_prize_senior_config["surplus_lock_count"] -= 1
                            #     act_prize_senior_config["modify_date"] = now_date
                            #     break
                            if int(senior_ability_config["type_id"]) == PrizeSeniorConfigType.强制出奖.value:
                                if lottery_prize["id"] == prize["id"]:
                                    act_prize_senior_config["is_lock"] = 1
                                act_prize_senior_config["modify_date"] = now_date
                                act_prize_senior_config["must_surplus_count"] -= 1
                                if act_prize_senior_config["must_surplus_count"] <= 0:
                                    act_prize_senior_config["is_lock"] = 0
                                    act_prize_senior_config["must_surplus_count"] = int(senior_ability_config["lock_count"])
                    last_act_prize_senior_config_list.append(act_prize_senior_config)

        return last_act_prize_senior_config_list

    def sync_prize_surplus(self, redis_init, business_base_model, module_id):
        """
        :description: 同步奖品库存到redis，注意：新产品都是后台直接同步，不需要调用当前方法，只有旧产品，为了兼容才需要在第一次同步库存
        :param redis_init:redis_init
        :param module_id:机台id
        :return: 
        :last_editors: HuangJingCan
        """
        hash_name = business_base_model.get_cache_key_act_prize_surplus_list(module_id)
        act_prize_model = ActPrizeExModel()
        act_prize_list = act_prize_model.get_list(f"module_id={module_id} and is_del=0")
        for item in act_prize_list:
            redis_init.hincrby(hash_name, str(item.id), item.surplus)


class LotteryPermitHandler(ClientBaseHandler):
    """
    @description: 抽奖许可判断
    """
    @filter_check_params("act_id,login_token,module_id,lottery_type,asset_type")
    def get_async(self):
        """
        :description: 获取抽奖许可
        :param login_token:登录令牌
        :param act_id:活动id
        :param module_id: 机台id
        :param lottery_type：抽奖模式（1单抽2连抽3全收）
        :param asset_type：抽奖类型（2积分，3价格档位次数）
        :return: 抽奖
        :last_editors: ChenCheng
        """
        open_id = self.get_open_id()
        app_id = self.get_source_app_id()
        login_token = self.get_param("login_token")
        act_id = self.get_param_int("act_id")
        module_id = self.get_param_int("module_id")
        lottery_type = self.get_param_int("lottery_type", 1)
        asset_type = self.get_param_int("asset_type")
        now_date = self.get_now_datetime()

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        machine_info_model = ActModuleExModel(db_transaction=db_transaction, context=self)
        act_info_model = ActInfoModel(context=self)
        act_info_ex_model = ActInfoExModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        redis_init = SevenHelper.redis_init()

        #请求太频繁限制
        if self.check_continue_request("Lottery_Permit", app_id, open_id) == False:
            return self.response_json_error("HintMessage", "哎呀~当前操作人数过多")
        if lottery_type == 3:
            if self.check_continue_request("All_Lottery_Post", app_id, module_id, 500) == False:
                return self.response_json_error("HintMessage2", "哎呀~当前操作人数过多")

        # 判断用户资质
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.response_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.response_json_error("UserState", "对不起，你是黑名单用户,无法抽扭蛋")
        if user_info.login_token != login_token:
            return self.response_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽扭蛋")
        if not user_info.user_nick:
            return self.response_json_error("ErrorUserNick", "对不起，用户未授权")
        user_id = user_info.user_id
        user_nick = user_info.user_nick

        # 判断活动信息
        key_act_info = business_base_model.get_cache_key_act_info(act_id)
        act_info = act_info_model.get_cache_entity_by_id(act_id, dependency_key=key_act_info, cache_expire=1800)
        act_info_ex = act_info_ex_model.get_cache_entity_by_id(act_id, dependency_key=key_act_info, cache_expire=1800)
        if not act_info or not act_info_ex or act_info.is_release == 0 or act_info.is_del == 1:
            return self.response_json_error("NoAct", "对不起，活动不存在")
        if now_date < act_info.start_date:
            return self.response_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        if now_date > act_info.end_date:
            return self.response_json_error("NoAct", "活动已结束")

        #获取机台信息
        key_act_module = business_base_model.get_cache_key_act_module(module_id)
        machine_info = machine_info_model.get_cache_entity_by_id(module_id, dependency_key=key_act_module, cache_expire=1800)
        if not machine_info or machine_info.is_release == 0:
            return self.response_json_error("NoMachine", "对不起，机台不存在")
        if machine_info.start_date == "1900-01-01 00:00:00":
            sale_date = now_date
        else:
            sale_date = str(machine_info.start_date)
        sale_date = TimeHelper.format_time_to_datetime(sale_date)
        if TimeHelper.format_time_to_datetime(now_date) < sale_date:
            china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
            return self.response_json_error("NoAct", "机台将在" + china_sale_date + "开售,敬请期待~")
        if machine_info.end_date != "1900-01-01 00:00:00" and now_date > machine_info.end_date:
            return self.response_json_error("NoAct", "机台已下架")
        if (asset_type != 2 and machine_info.module_type == 2) or (asset_type != 3 and machine_info.module_type == 1):
            return self.response_json_error("ErrorType", "对不起，抽奖失败")

        if lottery_type == 1 or lottery_type == 2:
            # 单日抽奖次数限制
            if machine_info.is_limit_lottery_times > 0:
                now_day = SevenHelper.get_now_day_int()
                hash_name = f"lottery_limit_list:moduleid_{module_id}"
                key_lottery_limit = f"openid_{open_id}_day_{now_day}_type_{lottery_type}"
                button_count = redis_init.hget(hash_name, key_lottery_limit)
                button_count = button_count if button_count else 0
                if button_count:
                    if lottery_type == 1 and machine_info.single_lottery_limit and machine_info.single_lottery_limit <= button_count:
                        return self.response_json_error("LimitLottery1", "今日该抽赏次数已达上限，明日再来继续抽赏吧！")
                    if lottery_type == 2 and machine_info.continuous_lottery_limit and machine_info.continuous_lottery_limit <= button_count:
                        return self.response_json_error("LimitLottery2", "今日该抽赏次数已达上限，明日再来继续抽赏吧！")

        elif lottery_type == 3:
            if not machine_info.is_open_all_lottery:
                return self.response_json_error("NoOpenAllLottery", "对不起，全收未开启")

        # 相关数据存入redis
        lottery_data = {}
        lottery_data["app_id"] = app_id
        lottery_data["act_id"] = act_id
        lottery_data["user_id"] = user_id
        lottery_data["user_nick"] = user_nick
        lottery_data["asset_type"] = asset_type
        lottery_data["module_id"] = module_id
        lottery_data["lottery_type"] = lottery_type
        lottery_data["act_is_open_buy_back"] = act_info_ex.is_open_buy_back
        lottery_data["user_info_id"] = user_info.id
        lottery_data["open_id"] = open_id

        lottery_permit = "request_code_" + str(self.request_code)
        hash_name = f"lottery_permit_list:openid_{open_id}"
        expire_time = 3600 * 24  # 抽奖许可10秒过期 todo  测试阶段暂时设长时间过期
        redis_init.hset(hash_name, lottery_permit, SevenHelper.json_dumps(lottery_data))
        redis_init.expire(hash_name, expire_time)

        return self.response_json_success({"lottery_permit": lottery_permit})


class TestLotteryHandler(ClientBaseHandler):
    """
    :description: 试一试抽奖
    """
    @filter_check_params("act_id,login_token,module_id")
    def get_async(self):
        """
        :description: 抽奖
        :param login_token:登录令牌
        :param act_id:活动id
        :param module_id:机台id
        :return: 抽奖
        :last_editors: HuangJingCan
        """
        open_id = self.get_open_id()
        app_id = self.get_source_app_id()
        login_token = self.get_param("login_token")
        act_id = self.get_param_int("act_id")
        module_id = self.get_param_int("module_id")
        now_date = self.get_now_datetime()

        act_info_model = ActInfoModel(context=self)
        act_info_ex_model = ActInfoExModel(context=self)
        user_info_model = UserInfoModel(context=self)
        act_prize_model = ActPrizeExModel(context=self)
        machine_info_model = ActModuleExModel(context=self)
        business_base_model = BusinessBaseModel(context=self)
        frame_base_model = FrameBaseModel(context=self)

        # #请求太频繁限制 --- 如果有需求再加，正常限流完到这里已经不需要限制了
        # if self.check_continue_request("Lottery_Post", app_id, open_id, 100) == False:
        #     return self.response_json_error("HintMessage", "哎呀~当前操作人数过多")
        # if self.check_continue_request("All_Lottery_Post", app_id, module_id, 100) == False:
        #     return self.response_json_error("HintMessage2", "哎呀~当前操作人数过多")

        # 判断用户资质
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.response_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.response_json_error("UserState", "对不起，你是黑名单用户,无法抽扭蛋")
        # if user_info.login_token != login_token:
        #     return self.response_json_error("ErrorToken", "对不起，已在另一台设备登录,无法抽扭蛋")

        # 判断活动信息
        dependency_key = business_base_model.get_cache_key_act_info(act_id)
        act_info = act_info_model.get_cache_entity_by_id(act_id, dependency_key=dependency_key, cache_expire=1800)
        act_info_ex = act_info_ex_model.get_cache_entity_by_id(act_id, dependency_key=dependency_key, cache_expire=1800)
        if not act_info or not act_info_ex or act_info.is_release == 0 or act_info.is_del == 1:
            return self.response_json_error("NoAct", "对不起，活动不存在")
        if now_date < act_info.start_date:
            return self.response_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        if now_date > act_info.end_date:
            return self.response_json_error("NoAct", "活动已结束")

        #获取机台信息
        machine_dependency_key = business_base_model.get_cache_key_act_module(module_id)
        machine_info = machine_info_model.get_cache_entity_by_id(module_id, dependency_key=machine_dependency_key, cache_expire=1800)
        if not machine_info or machine_info.is_release == 0:
            return self.response_json_error("NoMachine", "对不起，机台不存在")
        if machine_info.start_date == "1900-01-01 00:00:00":
            sale_date = now_date
        else:
            sale_date = str(machine_info.start_date)
        sale_date = TimeHelper.format_time_to_datetime(sale_date)
        if TimeHelper.format_time_to_datetime(now_date) < sale_date:
            china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
            return self.response_json_error("NoAct", "机台将在" + china_sale_date + "开售,敬请期待~")
        if machine_info.end_date != "1900-01-01 00:00:00" and now_date > machine_info.end_date:
            return self.response_json_error("NoAct", "机台已下架")

        prize_dependency_key = f"act_prize_list:_moduleid_{module_id}"

        # 获取机台奖品
        act_prize_list = act_prize_model.get_cache_dict_list("module_id=%s and is_del=0 and is_release=1 and yfs_type=1 and surplus>0", order_by="sort_index desc", params=[module_id], dependency_key=prize_dependency_key, cache_expire=1800)

        if not act_prize_list:
            return self.response_json_error("NoPrize_02", "对不起，奖品库存不足")

        # 试一试按照实际概率出奖
        # lottery_prize = frame_base_model.lottery_algorithm_probability(act_prize_list)
        # 试一试按照平均概率出奖
        lottery_prize = act_prize_list[random.randint(0, len(act_prize_list) - 1)]

        if not lottery_prize:
            return self.response_json_error("NoPrize_03", "对不起，奖品库存不足")

        result = {}
        result["lottery_prize"] = lottery_prize

        #上报数据
        key_list_dict = {}
        key_list_dict_module = {}
        # 试一试人数（参与情况）
        key_list_dict["LotteryerTestUserCount"] = 1
        # 试一试次数（参与情况）
        key_list_dict["LotteryerTestCount"] = 1
        # 机台试一试人数（参与情况）
        key_name = 'LotteryerTestUserCount_' + str(module_id)
        key_list_dict_module[key_name] = 1
        # 机台试一试次数（参与情况）
        key_name = 'LotteryerTestCount_' + str(module_id)
        key_list_dict_module[key_name] = 1
        stat_base_model = StatBaseModel(context=self)
        stat_base_model.add_stat_list(app_id, act_id, 0, user_info.user_id, open_id, key_list_dict)
        stat_base_model.add_stat_list(app_id, act_id, module_id, user_info.user_id, open_id, key_list_dict_module)

        return self.response_json_success(result)


class LotteryReportHandler(ClientBaseHandler):
    """
    :description: 抽奖上报
    """
    @filter_check_params("act_id,module_id,lottery_type,lottery_count")
    def get_async(self):
        """
        :description: 抽奖上报
        :param act_id:活动id
        :param module_id:机台id
        :param lottery_type:抽奖类型：1单抽2连抽3全收4试一试
        :param lottery_count:抽奖次数
        :return: response_json_success
        :last_editors: HuangJingCan
        """
        app_id = self.get_source_app_id()
        open_id = self.get_open_id()
        act_id = self.get_param_int("act_id")
        module_id = self.get_param_int("module_id")
        lottery_type = self.get_param_int("lottery_type", 1)
        lottery_count = self.get_param_int("lottery_count", 1)

        machine_info_model = ActModuleExModel(context=self)
        act_info_model = ActInfoModel(context=self)
        stat_base_model = StatBaseModel(context=self)
        user_info_model = UserInfoModel(context=self)
        business_base_model = BusinessBaseModel(context=self)

        dependency_key = business_base_model.get_cache_key_act_info(act_id)
        act_info = act_info_model.get_cache_entity_by_id(act_id, dependency_key=dependency_key, cache_expire=1800)
        if not act_info or act_info.is_release == 0 or act_info.is_del == 1:
            return self.response_json_error("NoAct", "对不起，活动不存在")

        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.response_json_error('NoUser', '对不起，用户不存在')
        user_id = user_info.user_id
        #获取机台信息
        dependency_key_machine = business_base_model.get_cache_key_act_module(module_id)
        machine_info = machine_info_model.get_cache_entity_by_id(module_id, dependency_key=dependency_key_machine)
        if not machine_info:
            return self.response_json_error("NoAct", "对不起，机台不存在")
        #上报数据
        key_list_dict = {}
        key_list_dict_module = {}
        # 总抽赏人数（活动数据）
        key_list_dict["TotalLotteryUserCount"] = 1
        # 赏品发放数量（活动数据）
        key_list_dict["TotalRawardPrizeCount"] = lottery_count
        # 总抽赏人数 （参与情况）
        key_list_dict["LotteryUserCount"] = 1
        # 总抽赏次数 （参与情况）
        key_list_dict["LotteryCount"] = lottery_count
        # 机台总抽赏人数 （参与情况）
        key_name = 'LotteryUserCount_' + str(module_id)
        key_list_dict_module[key_name] = 1
        # 机台总抽赏次数 （参与情况）
        key_name = 'LotteryCount_' + str(module_id)
        key_list_dict_module[key_name] = lottery_count
        if lottery_type == 1:
            # 单抽人数 （参与情况）
            key_list_dict["LotteryFirstButtonUserCount"] = 1
            # 单抽单抽次数 （参与情况）
            key_list_dict["LotteryFirstButtonCount"] = 1
            # 机台单抽人数 （参与情况）
            key_name = 'LotteryFirstButtonUserCount_' + str(module_id)
            key_list_dict_module[key_name] = 1
            # 机台单抽次数 （参与情况）
            key_name = 'LotteryFirstButtonCount_' + str(module_id)
            key_list_dict_module[key_name] = 1
        elif lottery_type == 2:
            # 连抽人数（参与情况）
            key_list_dict["LotterySecondButtonUserCount"] = 1
            # 连抽次数（参与情况）
            key_list_dict["LotterySecondButtonCount"] = 1
            # 机台连抽人数（参与情况）
            key_name = 'LotterySecondButtonUserCount_' + str(module_id)
            key_list_dict_module[key_name] = 1
            # 机台连抽次数（参与情况）
            key_name = 'LotterySecondButtonCount_' + str(module_id)
            key_list_dict_module[key_name] = 1
        elif lottery_type == 3:
            # 全收人数（参与情况）
            key_list_dict["LotteryAllUserCount"] = 1
            # 全收次数（参与情况）
            key_list_dict["LotteryAllCount"] = 1
            # 机台全收人数（参与情况）
            key_name = 'LotteryAllUserCount_' + str(module_id)
            key_list_dict_module[key_name] = 1
            # 机台全收次数（参与情况）
            key_name = 'LotteryAllCount_' + str(module_id)
            key_list_dict_module[key_name] = 1
        # elif lottery_type == 4:
        #     # 试一试人数（参与情况）
        #     key_list_dict["LotteryerTestUserCount"] = 1
        #     # 试一试次数（参与情况）
        #     key_list_dict["LotteryerTestCount"] = 1
        #     # 机台试一试人数（参与情况）
        #     key_name = 'LotteryerTestUserCount_' + str(module_id)
        #     key_list_dict_module[key_name] = 1
        #     # 机台试一试次数（参与情况）
        #     key_name = 'LotteryerTestCount_' + str(module_id)
        #     key_list_dict_module[key_name] = 1

        stat_base_model.add_stat_list(app_id, act_id, 0, user_id, open_id, key_list_dict)
        stat_base_model.add_stat_list(app_id, act_id, module_id, user_id, open_id, key_list_dict_module)

        return self.response_json_success()