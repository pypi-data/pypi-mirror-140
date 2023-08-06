# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2022-02-17 11:13:49
@LastEditTime: 2022-02-23 14:34:15
@LastEditors: ChenCheng
:Description: 扭蛋机一番赏基础路由
"""
# 框架引用
from seven_framework.web_tornado.monitor import MonitorHandler
from seven_cloudapp_frame.handlers.server import *
from seven_cloudapp_frame.handlers.client import *
from seven_cloudapp_frame.handlers.core import *

from seven_cloudapp_ndjyfs.handlers.server import *
from seven_cloudapp_ndjyfs.handlers.client import *


def seven_cloudapp_ndjyfs_route():
    return [
        (r"/monitor", MonitorHandler),
        (r"/", IndexHandler),
        # 千牛端接口
        (r"/server/instant", app_s.InstantiateAppHandler),  # app实例化
        (r"/server/app_info", app_s.AppInfoHandler),  # 获取AppInfo
        (r"/server/app_update", app_s.VersionUpgradeHandler),  #小程序更新
        (r"/server/update_info", base_s.UpdateInfoHandler),  # 获取更新信息
        (r"/server/act_qrcode", act_s.CreateActQrCodeHandler),  # 获取活动二维码
        (r"/server/shop_power_config", app_s.GetHighPowerListHandler),  # 获取商家权限配置
        (r"/server/home_navigation", base_s.HomeNavigationHandler),  # 获取首页导航栏信息 
        (r"/server/launch_setting_info", base_s.LaunchSettingInfo),  # 投放页配置信息             
        (r"/server/login", user_s.LoginHandler),  # 商家登录登记
        (r"/server/act_type_list", act_s.ActTypeListHandler),  # 获取活动类型
        (r"/server/theme_list", theme_s.ThemeInfoListHandler),  # 获取主题列表
        (r"/server/skin_list", theme_s.SkinInfoListHandler),  #皮肤列表
        (r"/server/act_create", act_s.ActCreateHandler),  # 创建活动
        (r"/server/act", act_s.ActHandler),  # 修改活动首页配置信息
        (r"/server/act_other", act_s.ActOtherHandler),  # 修改活动其他配置信息
        (r"/server/act_info", act_s.ActInfoHandler),  # 获取活动信息
        (r"/server/ip_list", ip_s.IpInfoListHandler),  # 获取IP列表
        (r"/server/ip", ip_s.SaveIpInfoHandler),  # IP保存
        (r"/server/ip_del", ip_s.DeleteIpInfoHandler),  # 删除IP
        (r"/server/ip_release", ip_s.ReleaseIpInfoHandler),  # 上架下架IP
        # ------------------------------机台配置------------------------------
        (r"/server/machine_list", machine_s.MachineListHandler),  # 机台列表
        (r"/server/machine", machine_s.MachineHandler),  # 机台保存
        (r"/server/machine_del", machine_s.MachineDelHandler),  # 删除机台
        (r"/server/machine_release", machine_s.MachineReleaseHandler),  # 上架下架机台
        (r"/server/machine_copy", machine_s.MachineCopyHandler),  # 复制机台
        (r"/server/prize_list_export", prize_s.PrizeListExportHandler),  #批量导出奖品列表
        # ------------------------------价格挡位------------------------------
        (r"/server/update_machine_price", machine_s.UpdateMachinePriceHandler),  #更新机台价格
        (r"/server/price_list", price_s.PriceGearListHandler),  # 价格档位列表，回收站列表：传参is_del=1
        (r"/server/checking_price_gear", price_s.CheckPriceGearHandler),  # 验证价格档位
        (r"/server/price", price_s.SavePriceGearHandler),  # 价格档位保存  
        (r"/server/delete_price_gear", price_s.DeletePriceGearHandler),  # 价格档位删除
        (r"/server/review_price_gear", price_s.ReviewPriceGearHandler),  # 价格档位恢复
        # ------------------------------奖品------------------------------
        (r"/server/prize", prize_s.PrizeHandler),  # 奖品保存
        (r"/server/prize_list", prize_s.PrizeListHandler),  # 奖品列表
        (r"/server/prize_surplus", prize_s.PrizeSurplusHandler),  # 修改奖品库存
        (r"/server/prize_probability", prize_s.PrizeProbabilityHandler),  # 修改奖品权重
        (r"/server/prize_del", prize_s.PrizeDelHandler),  # 删除奖品
        (r"/server/prize_release", prize_s.PrizeReleaseHandler),  # 上架下架奖品     
        # (r"/server/prize_update_list", prize_s.PrizeUpdateListHandler),  # 批量修改列表
        (r"/server/update_goods_code", prize_s.UpdateGoodsCodeHandler),  # 修改商家编码 
        (r"/server/goods_list", goods_s.GoodsListHandler),  # 导入商品列表（获取当前会话用户出售中的商品列表）
        (r"/server/goods_list_goodsid", goods_s.GoodsListByGoodsIDHandler),  #获取淘宝商品列表
        (r"/server/goods_info", goods_s.GoodsInfoHandler),  #  获取商品信息
        # ------------------------------任务------------------------------
        (r"/server/task_list", task_s.TaskInfoListHandler),  #任务列表
        (r"/server/task", task_s.SaveTaskInfoHandler),  #保存任务
        # ------------------------------投放------------------------------
        (r"/server/init_launch_goods_list", launch_s.InitLaunchGoodsHandler),  #初始化活动投放
        (r"/server/init_launch_goods_callback", launch_s.InitLaunchGoodsCallBackHandler),  #初始化投放商品回调接口 -- 未知是否使用
        (r"/server/save_launch_goods_status", launch_s.UpdateLaunchGoodsStatusHandler),  #保存更改投放商品的状态
        (r"/server/launch_goods_list", launch_s.LaunchGoodsListHandler),  #投放商品列表
        (r"/server/async_launch_goods", launch_s.AsyncLaunchGoodsHandler),  #同步投放商品列表
        # ------------------------------数据概览------------------------------
        (r"/server/report_total", report_s.ReportTotalHandler),  # 报表数据列表(首行)
        (r"/server/report_info", report_s.StatReportListHandler),  # 报表数据列表(表格)
        (r"/server/report_list", report_s.TrendReportListHandler),  # 趋势图数据
        # ------------------------------用户、订单相关------------------------------
        (r"/server/user_list", user_s.UserListHandler),  # 用户列表
        (r"/server/update_user_status", user_s.UpdateUserStatusHandler),  # 更新用户状态
        (r"/server/user_asset_log", user_s.AssetLogListHandler),  # 用户资产流水记录（包含次数和积分）
        (r"/server/update_user_asset_list", user_s.UpdateUserAssetListHandler),  # 变更用户资产（包含次数和积分）
        (r"/server/user_price_gear_list", user_s.UserPriceGeartListHandler),  # 获取用户资产信息
        (r"/server/prize_order_list", order_s.PrizeOrderListHandler),  # 发货订单表 
        (r"/server/prize_order_export", order_s.PrizeOrderExportHandler),  # 发货订单表导出
        (r"/server/prize_roster_list", order_s.PrizeRosterListHandler),  # 背包奖品列表
        (r"/server/prize_order_status", order_s.UpdatePrizeOrderStatusHandler),  #更新用户奖品订单状态（填写发货、不予发货）
        (r"/server/prize_order_remarks", order_s.UpdatePrizeOrderSellerRemarkHandler),  #更新用户奖品订单备注
        (r"/server/hide_prize_roster", order_s.HidePrizeRosterHandler),  # 隐藏用户奖品
        (r"/server/prize_roster_export", order_s.PrizeRosterListExportHandler),  #批量导出奖品列表
        (r"/server/prize_order_import", order_s.ImportPrizeOrderHandler),  #订单导入
        (r"/server/pay_order_list", order_s.PayOrderListHandler),  # 支付订单
        (r"/server/pay_order_export", order_s.TaoPayOrderExportHandler),  # 支付订单导出
        (r"/server/buy_back_list", order_s.BuyBackListHandler),  # 回购奖品表
        (r"/server/buy_back_export", order_s.BuyBackListExportHandler),  # 批量导出回购奖品表
        (r"/server/presale_prize_list", order_s.PresalePrizeListHandler),  # 预售奖品表
        (r"/server/presale_prize_export", order_s.PresalePrizeListExportHandler),  # 批量导出预售奖品表
        (r"/server/presale_prize_config_list", order_s.PresalePrizeConfigListHandler),  # 预售奖品配置表
        (r"/server/deliver_sale_prize", order_s.DeliverSalePrizeHandler),  # 发售预售奖品
        # ----------------------------------------------------------------------------------------------------------------客户端接口接口
        # 客户端接口
        (r"/client/shop_power_config", app.GetHighPowerListHandler),  # 获取商家权限配置
        (r"/client/login", user.LoginHandler),  # 用户登录 
        (r"/client/user", user.UpdateUserInfoHandler),  # 用户更新
        (r"/client/user_asset_list", user.UserAssetListHandler),  # 用户资产列表
        (r"/client/theme_list", theme.ThemeInfoListHandler),  # 获取主题列表 
        (r"/client/check_is_member", user.CheckIsMemberHandler),  # 判断用户是否是会员
        (r"/client/get_join_member_url", user.GetJoinMemberUrlHandler),  #加入会员地址
        (r"/client/sync_pay_order", user.SyncPayOrderHandler),  # 支付订单获取次数和运费券
        (r"/client/address", address.AddressInfoListHandler),  #省市区
        (r"/client/act_info", act.ActInfoHandler),  # 获取活动信息  
        (r"/client/ip_list", act.IpListHandler),  # 获取ip列表
        (r"/client/module_list", act.ActModuleListHandler),  # 获取机台列表
        (r"/client/price_gear_list", act.PriceGearListHandler),  # 获取价格档位列表
        (r"/client/prize_list", prize.PrizeListHandler),  # 获取机台奖品列表
        (r"/client/yfs_prize_total", prize.YfsPrizeTotalHandler),  # 获取一番赏奖品统计
        (r"/client/prize_total_surplus", prize.PrizeTotalSurplusHandler),  # 获取奖品库存
        (r"/client/prize_roster_list", prize.PrizeRosterListHandler),  # 获取机台中奖列表
        (r"/client/presale_prize_notice", prize.PresalePrizeNoticeHandler),  # 预售奖品开售通知
        (r"/client/special_prize_notice", prize.SpecialPrizeNoticeHandler),  # 特殊奖品发放通知
        (r"/client/update_special_prize_notice", prize.UpdateSpecialPrizeNoticeHandler),  # 更新特殊奖品发放通知
        (r"/client/user_prize_list", prize.UserPrizeListHandler),  # 获取用户奖品列表(背包)  --  包含已下单和可回购列表
        (r"/client/backpack_red", prize.BackpackRedHandler),  #获取用户背包红点接口（判断是否存在未下单奖品）
        (r"/client/prize_order_list", prize.PrizeOrderHandler),  #获取奖品订单列表
        (r"/client/buy_back_prize", prize.BuyBackPrizeHandler),  # 奖品主动回购获得积分
        (r"/client/choice_prize_sku", prize.ChoicePrizeSkuHandler),  #选择奖品sku
        (r"/client/submit_prize_order", prize.SubmitPrizeOrderHandler),  # 下单接口
        (r"/client/goods_info", goods.SkuInfoHandler),  #  获取商品SKU信息
        (r"/client/task_list", task.TaskInfoListHandler),  #任务列表
        (r"/client/weekly_sign", task.WeeklySignHandler),  #签到
        (r"/client/task_inivite", task.InviteNewUserHandler),  # 邀请上报
        (r"/client/task_member", task.JoinMemberHandler),  # 加入会员
        (r"/client/task_collect", task.CollectGoodsHandler),  # 收藏商品
        (r"/client/task_browse", task.BrowseGoodsHandler),  # 浏览商品
        (r"/client/task_favor", task.FavorStoreHandler),  #关注店铺奖励
        (r"/client/task_exchange", task.ExchangeIntegralHandler),  # 消费兑换积分
        (r"/client/task_receive_reward", task.ReceiveRewardHandler),  # 奖励接口（点击领取奖励）
        (r"/client/share_report", stat.ShareReportHandler),  #用户分享上报
        (r"/client/invite_report", stat.InviteReportHandler),  #邀请进入上报
        # 抽奖相关
        (r"/client/lottery_permit", lottery.LotteryPermitHandler),  #抽奖许可
        (r"/client/lottery", lottery.LotteryHandler),  #抽奖
        (r"/client/all_lottery", lottery.ALLLotteryHandler),  #全收
        (r"/client/test_lottery", lottery.TestLotteryHandler),  #试一试
        (r"/client/lottery_report", lottery.LotteryReportHandler),  #抽奖成功上报
    ]