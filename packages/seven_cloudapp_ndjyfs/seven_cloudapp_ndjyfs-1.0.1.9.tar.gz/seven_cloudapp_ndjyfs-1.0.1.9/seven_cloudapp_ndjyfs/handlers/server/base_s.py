# -*- coding: utf-8 -*-
"""
@Author: HuangJingCan
@Date: 2021-05-28 18:27:06
@LastEditTime: 2022-02-23 16:15:22
@LastEditors: ChenCheng
@Description: 
"""
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.ip_base_model import *

from seven_cloudapp_frame.models.db_models.base.base_info_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.product.product_price_model import *
from seven_cloudapp_frame.models.db_models.saas.saas_custom_model import *


class HomeNavigationHandler(ClientBaseHandler):
    """
    :description: 首页导航栏
    """
    def get_async(self):
        """
        :description: 获取首页所有有需要的公用信息
        :param {*}
        :return 字典
        :last_editors: HuangJingCan
        """
        user_nick = self.get_user_nick()
        app_id = self.get_source_app_id()
        access_token = self.get_param("access_token")
        is_log = bool(self.get_param("is_log", False))
        app_key, app_secret = self.get_app_key_secret()
        # app_id = self.get_param("app_id")

        if not user_nick:
            return self.response_json_error("Error", "对不起,请先授权登录")
        store_user_nick = user_nick.split(':')[0]
        if not store_user_nick:
            return self.response_json_error("Error", "对不起，请先授权登录")
        base_info = BaseInfoModel(context=self).get_dict()
        if not base_info:
            return self.response_json_error("BaseInfoError", "基础信息出错")

        app_info = None
        if app_id:
            app_info = AppInfoModel(context=self).get_dict("app_id=%s", params=app_id)
        top_base_model = TopBaseModel(context=self)

        # 左上角信息
        info = {}
        info["company"] = "天志互联"
        info["miniappName"] = base_info["product_name"]
        info["logo"] = base_info["product_icon"]

        # 左边底部菜单
        helper_info = {}
        helper_info["customer_service"] = base_info["customer_service"]
        helper_info["video_url"] = base_info["video_url"]
        helper_info["study_url"] = base_info["study_url"]
        helper_info["is_remind_phone"] = base_info["is_remind_phone"]
        helper_info["phone"] = ""
        s4 = self.json_loads(base_info["s4"])
        helper_info["launch_setting_url"] = s4["launch_setting_url"] + str(app_id)
        helper_info["data_analysis_url"] = s4["data_analysis_url"] + str(app_id)
        # 帮助信息
        helper_info["course_url"] = base_info["course_url"]

        # 过期时间
        renew_info = {}
        renew_info["surplus_day"] = 0
        dead_date = ""
        # self.logging_link_info("【app_key||app_secret||store_user_nick】:" + str(app_key) + "||" + str(app_secret) + "||" + str(store_user_nick))
        if app_info:
            helper_info["phone"] = app_info["app_telephone"]
            dead_date = app_info["expiration_date"]
        else:
            dead_date = top_base_model.get_dead_date(store_user_nick, access_token, app_key, app_secret, is_log)
            dead_date = dead_date.data
        renew_info["dead_date"] = dead_date
        if dead_date != "expire":
            renew_info["surplus_day"] = TimeHelper.difference_days(dead_date, self.get_now_datetime())

        data = {}
        data["app_info"] = info
        data["helper_info"] = helper_info
        data["renew_info"] = renew_info
        product_price = ProductPriceModel(context=self).get_dict()
        if product_price:
            data["renew_prices"] = self.json_loads(product_price["content"])

        return self.response_json_success(data)


class UpdateInfoHandler(ClientBaseHandler):
    """
    :description: 获取更新信息
    """
    @filter_check_params("app_id")
    def get_async(self):
        """
        :description: 获取更新信息
        :param app_id：app_id
        :return dict
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")

        base_info = BaseInfoModel(context=self).get_entity()
        if not base_info:
            return self.response_json_error("BaseInfoError", "基础信息出错")
        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.response_json_error("AppInfoError", "App信息出错")

        data = {}

        data["client_ver"] = base_info.client_ver
        #指定账号升级
        test_client_ver = config.get_value("test_client_ver")
        if test_client_ver:
            user_nick = self.get_user_nick()
            if user_nick:
                if user_nick == config.get_value("test_user_nick"):
                    data["client_ver"] = test_client_ver

        data["server_ver"] = base_info.server_ver
        data["client_now_ver"] = app_info.template_ver
        data["is_force_update"] = base_info.is_force_update
        data["update_function"] = []
        if base_info.update_function:
            data["update_function"] = self.json_loads(base_info.update_function)
        data["update_function_b"] = []
        if base_info.update_function_b:
            data["update_function_b"] = self.json_loads(base_info.update_function_b)
        return self.response_json_success(data)


class LaunchSettingInfo(ClientBaseHandler):
    """
    :description: 投放页配置信息        
    """
    @filter_check_params("app_id,act_id")
    def get_async(self):
        """
        :description:投放页配置信息
        :param app_id:app_id
        :param act_id：活动id
        :return 
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        act_id = self.get_param_int("act_id")
        is_open_theme_page = self.get_param_int("is_open_theme_page")

        if act_id <= 0:
            return self.response_json_error("ActError", "无效活动")

        app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
        if not app_info:
            return self.response_json_error("AppInfoError", "App信息出错")

        base_info = BaseInfoModel(context=self).get_dict()
        if not base_info:
            return self.response_json_error("BaseInfoError", "基础信息出错")

        # 投放模块数据
        data = {}
        data = self.json_loads(base_info["decoration_poster_json"])
        # 小程序链接
        data["online_url"] = self.get_online_url(act_id, app_id)
        data["live_url"] = self.get_live_url(app_id)
        # 判断是否开启高级功能：主题统一页
        if is_open_theme_page == 0:
            page_list, total = IpBaseModel(context=self).get_ip_info_list(app_id, act_id, 0, 1, "id", is_cache=False)
            if page_list:
                data["online_url"] += "," + str(page_list[0]['id'])
            else:
                data["online_url"] = ""
        # 小程序二维码
        url = data["online_url"]
        img, img_bytes = QRCodeHelper.create_qr_code(url, fill_color="black")
        img_base64 = base64.b64encode(img_bytes).decode()
        data["act_qrcode_url"] = f"data:image/jpeg;base64,{img_base64}"
        # 投放教程链接
        s4 = self.json_loads(base_info["s4"])
        data["launch_tutorials_link"] = s4["launch_tutorials_link"]

        return self.response_json_success(data)