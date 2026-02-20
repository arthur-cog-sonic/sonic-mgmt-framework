#!/usr/bin/python3
###########################################################################
#
# Copyright 2024 Broadcom. The term Broadcom refers to Broadcom Inc. and/or
# its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###########################################################################

import sys
import json
import cli_client as cc
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output


AAA_PATH = "/restconf/data/openconfig-aaa:aaa"
AAA_AUTHENTICATION_PATH = AAA_PATH + "/authentication"
AAA_AUTHORIZATION_PATH = AAA_PATH + "/authorization"
AAA_ACCOUNTING_PATH = AAA_PATH + "/accounting"


def check_response(resp):
    if not resp.ok():
        print(resp.error_message())
        return 1
    return 0


def bool_from_option(option):
    if option == "enable":
        return True
    elif option == "disable":
        return False
    elif option == "default":
        return False
    return False


def invoke(func, args):
    aa = cc.ApiClient()

    if func == "patch_openconfig_aaa_aaa_authentication_config_failthrough":
        keypath = cc.Path(AAA_AUTHENTICATION_PATH + "/config/failthrough")
        value = bool_from_option(args[0])
        body = {"openconfig-aaa:failthrough": value}
        return aa.patch(keypath, body)

    if func == "patch_openconfig_aaa_aaa_authentication_config_fallback":
        keypath = cc.Path(AAA_AUTHENTICATION_PATH + "/config/fallback")
        value = bool_from_option(args[0])
        body = {"openconfig-aaa:fallback": value}
        return aa.patch(keypath, body)

    if func == "patch_openconfig_aaa_aaa_authentication_config_debug":
        keypath = cc.Path(AAA_AUTHENTICATION_PATH + "/config/debug")
        value = bool_from_option(args[0])
        body = {"openconfig-aaa:debug": value}
        return aa.patch(keypath, body)

    if func == "patch_openconfig_aaa_aaa_authentication_config_authentication_method":
        keypath = cc.Path(AAA_AUTHENTICATION_PATH + "/config/authentication-method")
        methods = [m for m in args if m and m.strip()]
        body = {"openconfig-aaa:authentication-method": methods}
        return aa.patch(keypath, body)

    if func == "patch_openconfig_aaa_aaa_authorization_config_authorization_method":
        keypath = cc.Path(AAA_AUTHORIZATION_PATH + "/config/authorization-method")
        methods = [m for m in args if m and m.strip()]
        body = {"openconfig-aaa:authorization-method": methods}
        return aa.patch(keypath, body)

    if func == "patch_openconfig_aaa_aaa_accounting_config_accounting_method":
        keypath = cc.Path(AAA_ACCOUNTING_PATH + "/config/accounting-method")
        methods = [m for m in args if m and m.strip()]
        body = {"openconfig-aaa:accounting-method": methods}
        return aa.patch(keypath, body)

    if func == "delete_openconfig_aaa_aaa_authentication_config_failthrough":
        keypath = cc.Path(AAA_AUTHENTICATION_PATH + "/config/failthrough")
        return aa.delete(keypath)

    if func == "delete_openconfig_aaa_aaa_authentication_config_fallback":
        keypath = cc.Path(AAA_AUTHENTICATION_PATH + "/config/fallback")
        return aa.delete(keypath)

    if func == "delete_openconfig_aaa_aaa_authentication_config_debug":
        keypath = cc.Path(AAA_AUTHENTICATION_PATH + "/config/debug")
        return aa.delete(keypath)

    if func == "delete_openconfig_aaa_aaa_authentication_config_authentication_method":
        keypath = cc.Path(AAA_AUTHENTICATION_PATH + "/config/authentication-method")
        return aa.delete(keypath)

    if func == "delete_openconfig_aaa_aaa_authorization_config_authorization_method":
        keypath = cc.Path(AAA_AUTHORIZATION_PATH + "/config/authorization-method")
        return aa.delete(keypath)

    if func == "delete_openconfig_aaa_aaa_accounting_config_accounting_method":
        keypath = cc.Path(AAA_ACCOUNTING_PATH + "/config/accounting-method")
        return aa.delete(keypath)

    if func == "get_openconfig_aaa_aaa":
        keypath = cc.Path(AAA_PATH)
        api_response = aa.get(keypath, ignore404=True)
        if not api_response.ok():
            print(api_response.error_message())
            return api_response
        if api_response.content:
            show_cli_output(args[0], api_response.content)
        return api_response

    print("%Error: not implemented: " + func)
    return None


def run(func, args):
    resp = invoke(func, args)
    if resp is not None:
        check_response(resp)


if __name__ == "__main__":
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
