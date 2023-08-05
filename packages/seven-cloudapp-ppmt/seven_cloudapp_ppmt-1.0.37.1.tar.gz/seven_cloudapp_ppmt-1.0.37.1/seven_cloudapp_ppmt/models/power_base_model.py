# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-09-01 13:52:58
@LastEditTime: 2022-02-17 17:35:39
@LastEditors: HuangJianYi
@Description: 
"""
from seven_framework import *
from seven_top import top
from asq.initiators import query


class PowerBaseModel():
    """
    :description:  商家权限处理
    """
    def __init__(self,context=None):
        self.context = context

    def get_config_data(self,store_user_nick,access_token,app_key, app_secret):
        """
        :description: 获取项目编码
        :param num_iids：num_iids
        :param access_token：access_token
        :return 
        :last_editors: HuangJianYi
        """
        config_data = {}
        config_data["is_customized"] = 0
        config_data["name"] = ""
        config_data["project_code"] = ""
        shop_config_list = self.get_shop_config_list(store_user_nick)
        if len(shop_config_list) == 0:
            #获取项目编码
            project_code = self.get_project_code(store_user_nick, access_token, app_key, app_secret)
            project_code_list = self.get_project_code_list(project_code)
            if len(project_code_list) > 0:
                config_data["function_config_list"] = query(project_code_list[0]["function_info_second_list"]).select(lambda x: {"name": x["name"], "key_name": x["key_name"]}).to_list()
                config_data["skin_config_list"] = query(project_code_list[0]["skin_ids_second_list"]).select(lambda x: {"name": x["name"], "theme_id": x["theme_id"]}).to_list()
                config_data["name"] = project_code_list[0]["name"]
                config_data["project_code"] = project_code_list[0]["project_code"]
        else:
            config_data["function_config_list"] = query(shop_config_list[0]["function_info_second_list"]).select(lambda x: {"name": x["name"], "theme_id": x["theme_id"]}).to_list()
            config_data["skin_config_list"] = query(shop_config_list[0]["skin_ids_second_list"]).select(lambda x: {"name": x["name"], "theme_id": x["theme_id"]}).to_list()
            config_data["is_customized"] = 1
            config_data["name"] = "定制版"
        return config_data

    def get_project_code(self, store_user_nick, access_token, app_key, app_secret):
        """
        :description: 获取项目编码
        :param store_user_nick：商家主账号昵称
        :param access_token：access_token
        :return 
        :last_editors: HuangJianYi
        """
        try:
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.VasSubscribeGetRequest()

            req.article_code = config.get_value("article_code")
            req.nick = store_user_nick
            resp = req.getResponse(access_token)
            if "article_user_subscribe" not in resp["vas_subscribe_get_response"]["article_user_subscribes"].keys():
                return ""
            return resp["vas_subscribe_get_response"]["article_user_subscribes"]["article_user_subscribe"][0]["item_code"]
        except Exception as ex:
            self.context.logging_link_error(traceback.format_exc())
            return ""

    def get_project_code_list(self, project_code):
        """
        :description:  获取公共功能列表
        :param project_code:收费项目代码（服务管理-收费项目列表）
        :return list: 
        :last_editors: WangQiang
        """

        project_code_list = []
        if not project_code:
            return project_code_list
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return project_code_list
        requst_url = "http://taobao-mp-s.gao7.com/general/project_code_list"
        data = {}
        data["project_code"] = project_code
        data["product_id"] = product_id
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = json.loads(result.text)
            project_code_list = obj_data["Data"]
        return project_code_list

    def get_shop_config_list(self, store_user_nick):
        """
        :description:  获取店铺配置列表
        :param store_user_nick:商家主账号昵称
        :return list: 
        :last_editors: WangQiang
        """

        shop_config_list = []
        #产品id
        product_id = config.get_value("project_name")
        if not product_id:
            return shop_config_list
        requst_url = "http://taobao-mp-s.gao7.com/custom/query_skin_managemen_list"
        data = {}
        data["product_id"] = product_id
        data["store_user_nick"] = store_user_nick
        result = HTTPHelper.get(requst_url, data, {"Content-Type": "application/json"})
        if result and result.ok and result.text:
            obj_data = json.loads(result.text)
            shop_config_list = obj_data["Data"]
        return shop_config_list