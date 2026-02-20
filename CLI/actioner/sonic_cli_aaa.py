#!/usr/bin/python3
###########################################################################
#
# Copyright 2024 Broadcom. The term "Broadcom" refers to Broadcom Inc. and/or
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
from cli_client import ApiClient, Path
from rpipe_utils import pipestr
from scripts.render_cli import show_cli_output


def aaa_path(subpath=None):
    p = Path("/restconf/data/openconfig-system:system/aaa")
    if subpath:
        return p.join(subpath)
    return p


def check_ok(resp):
    if not resp.ok():
        print(resp.error_message())
        return 1
    return 0


def render(path, template):
    resp = ApiClient().get(path, ignore404=True)
    if not resp.ok():
        print(resp.error_message())
        return 1
    if resp.content:
        show_cli_output(template, resp.content)
    return 0


def parse_bool_option(option):
    if option == "enable":
        return True
    elif option == "disable":
        return False
    return None


def build_method_list(args):
    methods = []
    for a in args:
        a = a.strip()
        if a and a not in ("", "__params"):
            methods.append(a)
    return methods


class Handlers:
    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_config_failthrough(option, *args):
        if option == "default":
            resp = ApiClient().delete(
                aaa_path("authentication/config/openconfig-aaa-ext:failthrough")
            )
            return check_ok(resp)
        val = parse_bool_option(option)
        if val is None:
            print("%Error: Invalid option: {}".format(option))
            return 1
        body = {
            "openconfig-aaa:aaa": {
                "authentication": {
                    "config": {
                        "openconfig-aaa-ext:failthrough": val
                    }
                }
            }
        }
        resp = ApiClient().patch(aaa_path(), body)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_config_fallback(option, *args):
        if option == "default":
            resp = ApiClient().delete(
                aaa_path("authentication/config/openconfig-aaa-ext:fallback")
            )
            return check_ok(resp)
        val = parse_bool_option(option)
        if val is None:
            print("%Error: Invalid option: {}".format(option))
            return 1
        body = {
            "openconfig-aaa:aaa": {
                "authentication": {
                    "config": {
                        "openconfig-aaa-ext:fallback": val
                    }
                }
            }
        }
        resp = ApiClient().patch(aaa_path(), body)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_config_debug(option, *args):
        if option == "default":
            resp = ApiClient().delete(
                aaa_path("authentication/config/openconfig-aaa-ext:debug")
            )
            return check_ok(resp)
        val = parse_bool_option(option)
        if val is None:
            print("%Error: Invalid option: {}".format(option))
            return 1
        body = {
            "openconfig-aaa:aaa": {
                "authentication": {
                    "config": {
                        "openconfig-aaa-ext:debug": val
                    }
                }
            }
        }
        resp = ApiClient().patch(aaa_path(), body)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_config_authentication_method(*args):
        cleaned = [a for a in args if a and a.strip() and a.strip() != "__params"]
        if not cleaned:
            print("%Error: At least one authentication method required")
            return 1

        if "default" in cleaned:
            resp = ApiClient().delete(
                aaa_path("authentication/config/authentication-method")
            )
            return check_ok(resp)

        methods = build_method_list(cleaned)
        if not methods:
            print("%Error: No valid authentication methods provided")
            return 1

        body = {
            "openconfig-aaa:aaa": {
                "authentication": {
                    "config": {
                        "authentication-method": methods
                    }
                }
            }
        }
        resp = ApiClient().patch(aaa_path(), body)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authorization_config_authorization_method(*args):
        cleaned = [a for a in args if a and a.strip() and a.strip() != "__params"]
        if not cleaned:
            print("%Error: At least one authorization method required")
            return 1

        methods = build_method_list(cleaned)
        if not methods:
            print("%Error: No valid authorization methods provided")
            return 1

        body = {
            "openconfig-aaa:aaa": {
                "authorization": {
                    "config": {
                        "authorization-method": methods
                    }
                }
            }
        }
        resp = ApiClient().patch(aaa_path(), body)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_accounting_config_accounting_method(*args):
        cleaned = [a for a in args if a and a.strip() and a.strip() != "__params"]
        if not cleaned:
            print("%Error: At least one accounting method required")
            return 1

        if "disable" in cleaned:
            resp = ApiClient().delete(
                aaa_path("accounting/config/accounting-method")
            )
            return check_ok(resp)

        methods = build_method_list(cleaned)
        if not methods:
            print("%Error: No valid accounting methods provided")
            return 1

        body = {
            "openconfig-aaa:aaa": {
                "accounting": {
                    "config": {
                        "accounting-method": methods
                    }
                }
            }
        }
        resp = ApiClient().patch(aaa_path(), body)
        return check_ok(resp)

    @staticmethod
    def get_openconfig_aaa_aaa(template, *args):
        return render(aaa_path(), template)


def run(func, args):
    return getattr(Handlers, func)(*args)


if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
