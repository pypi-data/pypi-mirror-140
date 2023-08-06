# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-12 20:04:54
:LastEditTime: 2022-02-17 10:41:20
:LastEditors: HuangJingCan
:description: 活动相关
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.act_base_model import *

from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.base.base_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.theme.theme_info_model import *
from seven_cloudapp_frame.models.db_models.skin.skin_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_type_model import *
from seven_cloudapp_frame.models.db_models.act.act_prize_model import *

from seven_cloudapp_frame.handlers.server.act_s import ActTypeListHandler
from seven_cloudapp_frame.handlers.server.act_s import CreateActQrCodeHandler

from seven_cloudapp_ndjyfs.models.db_models.act.act_info_ex_model import *


class ActCreateHandler(ClientBaseHandler):
    """
    :description: 创建活动
    """
    @filter_check_params("app_id")
    def get_async(self):
        """
        :Description: 创建活动
        :param act_name：活动名称
        :param theme_id：主题id
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        owner_open_id = self.get_param("owner_open_id")
        # 暂时不需要的传参（由于后续可能扩展而保留，并使用默认值）
        act_name = self.get_param("act_name", "扭蛋一番赏")
        act_type = self.get_param_int("act_type", 4)  # 默认类型一番赏
        theme_id = self.get_param_int("theme_id")

        act_info_model = ActInfoModel(context=self)
        act_info_ex_model = ActInfoExModel(context=self)
        act_info = act_info_model.get_dict("app_id=%s", params=app_id)
        if act_info:
            act_info_ex = act_info_ex_model.get_dict("act_id=%s", params=act_info["id"])
            act_info.update(act_info_ex)
            return self.response_json_success(act_info)
        base_info = BaseInfoModel(context=self).get_entity()
        if not base_info:
            return self.response_json_error("BaseInfoError", "基础信息出错")
        theme_info = ThemeInfoModel(context=self).get_entity()
        if not theme_info:
            return self.response_json_error("NoTheme", "请管理员先上传主题信息")
        # 无皮肤配置
        # skin_info = SkinInfoModel(context=self).get_entity("theme_id=%s", params=theme_info.id)
        # if not skin_info:
        #     return self.response_json_error("NoSkin", "请管理员先上传皮肤信息")

        if not theme_id:
            theme_id = theme_info.id

        #初始化活动
        act_info, act_info_ex = self.initialize_act(app_id, owner_open_id, act_name, act_type, theme_id)

        # self.create_operation_log(OperationType.add.value, act_info.__str__(), "ActCreateHandler", None, self.json_dumps(act_info))
        act_id = act_info_model.add_entity(act_info)
        act_info_ex.act_id = act_id
        act_info_ex_model.add_entity(act_info_ex)

        act_info.id = act_id
        act_info.share_desc_json = self.json_loads(act_info.share_desc_json)
        act_info.rule_desc_json = self.json_loads(act_info.rule_desc_json)
        act_info_ex.notice_desc_json = self.json_loads(act_info_ex.notice_desc_json)
        act_info_ex.carousel_list = self.json_loads(act_info_ex.carousel_list)
        # act_info.online_url = self.get_online_url(act_info.id, act_info.app_id)
        # act_info.live_url = self.get_live_url(act_info.app_id)

        return self.response_json_success(act_info)

    def initialize_act(self, app_id, owner_open_id="", act_name="", act_type=1, theme_id=0, app_end_date=""):
        """
        :Description: 初始化活动
        :param app_id：app_id
        :param owner_open_id：主账号open_id
        :param act_name：活动名称
        :param act_type：活动类型：1购买玩法2权益玩法3一番赏
        :param theme_id：主题id
        :param app_end_date：app结束时间
        :return: 
        :last_editors: HuangJingCan
        """
        #基础信息
        base_info = BaseInfoModel(context=self).get_entity()
        #获取最后活动
        last_act_info = ActInfoModel(context=self).get_entity(order_by="sort_index desc")
        if theme_id == 0:
            #获取第一个主题 -- 基础表没有is_private字段，以及前端未定主题保存方式，暂时先注释掉
            # first_theme = ThemeInfoModel(context=self).get_entity("app_id=%s or is_private=0", order_by="sort_index", params=[app_id])
            first_theme = ThemeInfoModel(context=self).get_entity("app_id=%s ", order_by="sort_index", params=[app_id])
            theme_id = first_theme.id if first_theme else 0
        now_datetime = self.get_now_datetime()
        #增加默认活动
        act_info = ActInfo()
        act_info_ex = ActInfoEx()
        if last_act_info:
            act_info.sort_index = last_act_info.sort_index + 1
            if not act_name:
                act_info.act_name = (base_info.product_name + "_" + str(act_info.sort_index)) if base_info else "一番赏"
        #获取app结束时间
        if not app_end_date:
            app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=[app_id])
            if app_info:
                act_info.end_date = app_info.expiration_date
        else:
            act_info.end_date = app_end_date
        act_info.app_id = app_id
        act_info.act_type = act_type
        #默认主题ID 查询theme表得到
        act_info.theme_id = theme_id
        act_info.store_url = ""
        act_info.close_word = "抱歉，程序维护中"
        # act_info.currency_type = 1 if act_type == 1 else 2
        act_info.share_desc_json = {"taoword": "一番赏", "icon": [], "title": "一番赏", "desc": "一番赏"}
        act_info.share_desc_json = self.json_dumps(act_info.share_desc_json)
        act_info.rule_desc_json = [{"rule_title": "一番赏购买规则", "rule_detail": "在此填写规则"}]
        act_info.rule_desc_json = self.json_dumps(act_info.rule_desc_json)
        act_info.start_date = now_datetime
        act_info.is_black = 0  #是否开启黑名单
        act_info.refund_count = 0  #退款次数
        act_info.is_release = 1
        act_info.create_date = now_datetime
        act_info.modify_date = now_datetime
        # 扩展表
        #商家OpenID 查询appInfo表后得到
        act_info_ex.owner_open_id = owner_open_id
        act_info_ex.notice_desc_json = {"is_notice": 0, "notice_desc": "在此填写公告"}
        act_info_ex.notice_desc_json = self.json_dumps(act_info_ex.notice_desc_json)
        act_info_ex.step_configured = 0  #配置进度
        act_info_ex.carousel_list = []
        act_info_ex.carousel_list = self.json_dumps(act_info_ex.carousel_list)
        act_info_ex.is_del = 0
        act_info_ex.is_release = 1

        return act_info, act_info_ex


class ActInfoHandler(ClientBaseHandler):
    """
    :description: 活动信息获取
    """
    def get_async(self):
        """
        :description: 活动信息获取
        :param app_id：app_id
        :param act_id：活动id
        :return: 活动信息
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        act_id = self.get_param_int("act_id")

        act_info_model = ActInfoModel(context=self)
        act_info_ex_model = ActInfoExModel(context=self)

        act_info = None
        if act_id > 0:
            act_info = act_info_model.get_entity_by_id(act_id)
            act_info_ex = act_info_ex_model.get_entity_by_id(act_id)

        if act_info:
            act_info.share_desc_json = self.json_loads(act_info.share_desc_json)
            act_info.rule_desc_json = self.json_loads(act_info.rule_desc_json)
            act_info_ex.notice_desc_json = self.json_loads(act_info_ex.notice_desc_json)
            act_info_ex.carousel_list = self.json_loads(act_info_ex.carousel_list)
            # act_info.online_url = self.get_online_url(act_info.id, act_info.app_id)
            # act_info.live_url = self.get_live_url(act_info.app_id)

            # config_force = {}
            # act_info.force_config_json = self.json_loads(config_force)
            # config_freight = {}
            # act_info.freight_config_json = self.json_loads(config_freight)
            act_info_dict = act_info.__dict__
            act_info_dict.update(act_info_ex.__dict__)
            return self.response_json_success(act_info_dict)
        else:
            #初始化活动
            act_info, act_info_ex = ActCreateHandler(application=self.application, request=self.request).initialize_act(app_id)
            act_info.share_desc_json = self.json_loads(act_info.share_desc_json)
            act_info.rule_desc_json = self.json_loads(act_info.rule_desc_json)
            act_info_ex.notice_desc_json = self.json_loads(act_info_ex.notice_desc_json)
            act_info_ex.carousel_list = self.json_loads(act_info_ex.carousel_list)
            act_info_dict = act_info.__dict__
            act_info_dict.update(act_info_ex.__dict__)
            return self.response_json_success(act_info_dict)


class ActHandler(ClientBaseHandler):
    """
    :description: 修改活动首页配置
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 修改活动首页配置
        :param act_id：活动id
        :param act_name：活动名称
        :param theme_id：主题id
        :param finish_menu_config_json：当前步骤
        :param start_date：开始时间
        :param end_date：结束时间
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        act_id = self.get_param_int("act_id")
        act_name = self.get_param("act_name")
        theme_id = self.get_param_int("theme_id")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        step_configured = self.get_param_int("step_configured")
        now_date = self.get_now_datetime()

        act_info_model = ActInfoModel(context=self)
        act_info_ex_model = ActInfoExModel(context=self)
        base_info_model = BaseInfoModel(context=self)

        if act_id > 0:
            # 修改活动相关信息
            act_info = act_info_model.get_entity_by_id(act_id)
            act_info_ex = act_info_ex_model.get_entity_by_id(act_id)

            act_info.act_name = act_name
            act_info.theme_id = theme_id

            base_info = base_info_model.get_entity()
            if act_info.is_finish == 0:
                if base_info.i1 == step_configured:
                    act_info.is_finish = 1
            act_info.start_date = start_date
            act_info.end_date = end_date
            act_info.modify_date = now_date

            act_info_ex.step_configured = step_configured

            act_info_model.update_entity(act_info)
            act_info_ex_model.update_entity(act_info_ex)
            ActBaseModel(context=self)._delete_act_info_dependency_key(app_id, act_id)

        return self.response_json_success()


class ActOtherHandler(ClientBaseHandler):
    """
    :description: 修改活动其他配置
    """
    @filter_check_params("act_id")
    def post_async(self):
        """
        :description: 修改活动
        :param act_id：活动id
        :param is_release：是否发布
        :param close_word：关闭小程序文案
        :param share_desc_json：分享配置
        :param rule_desc_json：规则配置
        :param is_black：是否开启次数黑名单
        :param refund_count：退款成功次数
        :param finish_menu_config_json：当前步骤
        :param notice_desc_json:公告相关（开关加内容）
        :param is_open_buy_back：是否开启回购 ---高级功能：回购
        :param is_collection_shop_tips：是否收藏店铺提醒：0否1是
        :param collection_tips_type：是否强制收藏：0否1是
        :param is_force_collection：是否强制收藏：0否1是
        :param is_membership_tips：是否加入会员提醒：0否1是
        :param membership_tips_type：加入会员提示类型：1小程序启动时2抽奖时
        :param is_force_membership：是否强制加入会员：0否1是
        :param freight_goods_id：运费关联ID  ---高级功能：运费，有开就要传
        :param freight_price：运费券价格
        :param freight_statement：发货内页说明
        :param is_open_freight_free_num：是否开启满数量包邮
        :param freight_free_num：满数量包邮件数
        :param is_open_freight_free_price：是否开启满金额包邮
        :param freight_free_price：满金额包邮金额
        :param is_freight_free：是否无条件包邮
        :param freight_free_start_date：包邮活动开始时间
        :param freight_free_end_date：包邮活动结束时间
        :param carousel_list：首页轮播(数组)
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        act_id = self.get_param_int("act_id")
        is_release = self.get_param_int("is_release", 1)
        close_word = self.get_param("close_word")
        share_desc_json = self.get_param("share_desc_json", {})
        rule_desc_json = self.get_param("rule_desc_json", [])
        step_configured = self.get_param_int("step_configured")
        notice_desc_json = self.get_param("notice_desc_json", {})
        carousel_list = self.json_loads(self.get_param("carousel_list", []))
        is_black = self.get_param_int("is_black")
        refund_count = self.get_param_int("refund_count")
        # 高级功能传参
        is_open_buy_back = self.get_param_int("is_open_buy_back")
        is_collection_shop_tips = self.get_param_int("is_collection_shop_tips")
        collection_tips_type = self.get_param_int("collection_tips_type", 1)
        is_force_collection = self.get_param_int("is_force_collection")
        is_membership_tips = self.get_param_int("is_membership_tips")
        membership_tips_type = self.get_param_int("membership_tips_type", 2)
        is_force_membership = self.get_param_int("is_force_membership")
        freight_goods_id = self.get_param_int("freight_goods_id")
        freight_price = float(self.get_param("freight_price", 0.00))
        freight_statement = self.get_param("freight_statement")
        is_open_freight_free_num = self.get_param_int("is_open_freight_free_num")
        freight_free_num = self.get_param_int("freight_free_num")
        is_open_freight_free_price = self.get_param_int("is_open_freight_free_price")
        freight_free_price = float(self.get_param("freight_free_price", 0.00))
        is_freight_free = self.get_param_int("is_freight_free")
        freight_free_start_date = self.get_param("freight_free_start_date", "1900-01-01 00:00:00")
        freight_free_end_date = self.get_param("freight_free_end_date", "1900-01-01 00:00:00")
        now_date = self.get_now_datetime()

        act_info_model = ActInfoModel(context=self)
        act_info_ex_model = ActInfoExModel(context=self)
        base_info_model = BaseInfoModel(context=self)

        if freight_goods_id and not freight_price:
            return self.response_json_error("ErrorFreight", "运费券验证未通过")

        if len(carousel_list) == 0:
            return self.response_json_error("NoCarousel", "首页轮播不能为空")

        if act_id > 0:
            # 修改活动相关信息
            act_info = act_info_model.get_entity_by_id(act_id)
            act_info_ex = act_info_ex_model.get_entity_by_id(act_id)

            if not act_info or not act_info_ex:
                return self.response_json_error("ErrorAct", "活动异常")

            act_info.is_release = is_release
            act_info.close_word = close_word
            act_info.share_desc_json = share_desc_json
            act_info.rule_desc_json = rule_desc_json
            # base_info = base_info_model.get_entity()
            # if act_info.is_finish == 0:
            #     if base_info.i1 == step_configured:
            #         act_info.is_finish = 1
            act_info.is_finish = 1
            act_info.is_black = is_black
            act_info.refund_count = refund_count
            act_info.modify_date = now_date
            #扩展表
            act_info_ex.carousel_list = self.json_dumps(carousel_list)

            act_info_ex.notice_desc_json = notice_desc_json
            act_info_ex.step_configured = step_configured
            act_info_ex.is_release = is_release

            #高级功能部分
            #回购开关
            act_info_ex.is_open_buy_back = is_open_buy_back

            # 强提醒弹窗
            act_info_ex.is_collection_shop_tips = is_collection_shop_tips
            act_info_ex.collection_tips_type = collection_tips_type
            act_info_ex.is_force_collection = is_force_collection
            act_info_ex.is_membership_tips = is_membership_tips
            act_info_ex.membership_tips_type = membership_tips_type
            act_info_ex.is_force_membership = is_force_membership

            # 运费相关
            act_info_ex.freight_goods_id = freight_goods_id
            act_info_ex.freight_price = freight_price
            act_info_ex.freight_statement = freight_statement
            act_info_ex.is_open_freight_free_num = is_open_freight_free_num
            act_info_ex.freight_free_num = freight_free_num
            act_info_ex.is_open_freight_free_price = is_open_freight_free_price
            act_info_ex.freight_free_price = freight_free_price
            act_info_ex.is_freight_free = is_freight_free
            act_info_ex.freight_free_start_date = freight_free_start_date
            act_info_ex.freight_free_end_date = freight_free_end_date

            act_info_ex_model.update_entity(act_info_ex)

            act_info_model.update_entity(act_info)

            # act_info = act_info.__dict__
            # act_info.update(act_info_ex.__dict__)
            ActBaseModel(context=self)._delete_act_info_dependency_key(app_id, act_id)

            return self.response_json_success()

        return self.response_json_error("ErrorAct", "活动异常")