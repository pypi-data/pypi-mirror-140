# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 13:51:10
@LastEditTime: 2022-02-24 16:38:44
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.mp_base_model import *
from seven_cloudapp_frame.models.push_base_model import *
from asq.initiators import query


class AppExpireHandler(ClientBaseHandler):
    """
    :description: 获取小程序是否过期未续费
    """
    def get_async(self):
        """
        :description: 获取小程序是否过期未续费
        :return info
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()

        app_base_model = AppBaseModel(context=self)
        invoke_result_data = app_base_model.get_app_expire(app_id)
        if invoke_result_data.success ==False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class AddWechatSubscribeHandler(ClientBaseHandler):
    """
    :description: 添加微信订阅次数
    """
    def get_async(self):
        """
        :description: 添加微信订阅次数
        :return info
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()

        push_base_model = PushBaseModel(context=self)
        invoke_result_data = push_base_model.add_wechat_subscribe(app_id)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)


class GetHighPowerListHandler(ClientBaseHandler):
    """
    :description: 获取中台配置的高级权限列表
    """
    def get_async(self):
        """
        :description: 获取中台配置的高级权限列表
        :return: list
        :last_editors: HuangJianYi
        """
        app_id = self.get_source_app_id()
        app_base_model = AppBaseModel(context=self)
        app_info_dict = app_base_model.get_app_info_dict(app_id)
        if not app_info_dict:
            return self.response_json_error("Error", "小程序不存在")
        store_user_nick = app_info_dict["store_user_nick"]
        access_token = app_info_dict["access_token"]
        config_data = {}
        config_data["is_customized"] = 0
        top_base_model = TopBaseModel(context=self)
        mp_base_model = MPBaseModel(context=self)
        custom_function_list = mp_base_model.get_custom_function_list(store_user_nick)
        if len(custom_function_list) == 0:
            app_key, app_secret = self.get_app_key_secret()
            #获取项目编码
            project_code = top_base_model.get_project_code(store_user_nick, access_token, app_key, app_secret)
            public_function_list = mp_base_model.get_public_function_list(project_code)
            if len(public_function_list) > 0:
                config_data["function_config_list"] = query(public_function_list[0]["function_info_second_list"]).select(lambda x: {"name": x["name"], "key_name": x["key_name"]}).to_list()
        else:
            config_data["is_customized"] = 1
            config_data["function_config_list"] = []
            custom_function_list = list(filter(lambda custom_function: custom_function["app_id"] == app_id, custom_function_list))
            if len(custom_function_list) > 0:
                config_data["function_config_list"] = query(custom_function_list[0]["function_info_second_list"]).select(lambda x: {"name": x["name"], "key_name": x["key_name"]}).to_list()
        self.response_json_success(config_data)