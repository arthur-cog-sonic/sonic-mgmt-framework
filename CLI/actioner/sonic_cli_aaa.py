#!/usr/bin/python3
###########################################################################
#
# Copyright 2019 Dell, Inc.
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


AAA_PATH = "/restconf/data/openconfig-system:system/aaa"


def aaa_path(subpath=None):
    """Construct AAA REST API path."""
    p = Path(AAA_PATH)
    if subpath:
        return p.join(subpath)
    return p


def check_ok(resp):
    """Check response and print error if not OK."""
    if not resp.ok():
        print(resp.error_message())
        return 1
    return 0


def option_to_bool(option):
    """Convert enable/disable option to boolean value."""
    if option == "enable":
        return True
    elif option == "disable":
        return False
    return None


def methods_to_list(method1, method2=None):
    """Convert method arguments to a list, filtering empty values."""
    methods = []
    if method1 and method1.strip():
        methods.append(method1)
    if method2 and method2.strip():
        methods.append(method2)
    return methods


class Handlers:
    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_failthrough(option, *args):
        """Set authentication failthrough option."""
        if option == "default":
            return Handlers.delete_openconfig_aaa_aaa_authentication_failthrough()

        val = option_to_bool(option)
        if val is None:
            print("Invalid option: {}".format(option))
            return 1

        path = aaa_path("authentication/config")
        body = {
            "openconfig-system:config": {
                "openconfig-system-ext:failthrough": val
            }
        }
        resp = ApiClient().patch(path, body)
        return check_ok(resp)

    @staticmethod
    def delete_openconfig_aaa_aaa_authentication_failthrough(*args):
        """Delete authentication failthrough setting (reset to default)."""
        path = aaa_path("authentication/config/openconfig-system-ext:failthrough")
        resp = ApiClient().delete(path)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_fallback(option, *args):
        """Set authentication fallback option."""
        if option == "default":
            return Handlers.delete_openconfig_aaa_aaa_authentication_fallback()

        val = option_to_bool(option)
        if val is None:
            print("Invalid option: {}".format(option))
            return 1

        path = aaa_path("authentication/config")
        body = {
            "openconfig-system:config": {
                "openconfig-system-ext:fallback": val
            }
        }
        resp = ApiClient().patch(path, body)
        return check_ok(resp)

    @staticmethod
    def delete_openconfig_aaa_aaa_authentication_fallback(*args):
        """Delete authentication fallback setting (reset to default)."""
        path = aaa_path("authentication/config/openconfig-system-ext:fallback")
        resp = ApiClient().delete(path)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_debug(option, *args):
        """Set authentication debug option."""
        if option == "default":
            return Handlers.delete_openconfig_aaa_aaa_authentication_debug()

        val = option_to_bool(option)
        if val is None:
            print("Invalid option: {}".format(option))
            return 1

        path = aaa_path("authentication/config")
        body = {
            "openconfig-system:config": {
                "openconfig-system-ext:debug": val
            }
        }
        resp = ApiClient().patch(path, body)
        return check_ok(resp)

    @staticmethod
    def delete_openconfig_aaa_aaa_authentication_debug(*args):
        """Delete authentication debug setting (reset to default)."""
        path = aaa_path("authentication/config/openconfig-system-ext:debug")
        resp = ApiClient().delete(path)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_trace(option, *args):
        """Set authentication trace option."""
        if option == "default":
            return Handlers.delete_openconfig_aaa_aaa_authentication_trace()

        val = option_to_bool(option)
        if val is None:
            print("Invalid option: {}".format(option))
            return 1

        path = aaa_path("authentication/config")
        body = {
            "openconfig-system:config": {
                "openconfig-system-ext:trace": val
            }
        }
        resp = ApiClient().patch(path, body)
        return check_ok(resp)

    @staticmethod
    def delete_openconfig_aaa_aaa_authentication_trace(*args):
        """Delete authentication trace setting (reset to default)."""
        path = aaa_path("authentication/config/openconfig-system-ext:trace")
        resp = ApiClient().delete(path)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authentication_login(method1, method2=None, *args):
        """Set authentication login methods."""
        methods = methods_to_list(method1, method2)
        if not methods:
            print("At least one authentication method is required")
            return 1

        path = aaa_path("authentication/config")
        body = {
            "openconfig-system:config": {
                "authentication-method": methods
            }
        }
        resp = ApiClient().patch(path, body)
        return check_ok(resp)

    @staticmethod
    def delete_openconfig_aaa_aaa_authentication_login(*args):
        """Delete authentication login methods (reset to default)."""
        path = aaa_path("authentication/config/authentication-method")
        resp = ApiClient().delete(path)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_authorization_login(method1, method2=None, *args):
        """Set authorization login methods."""
        methods = methods_to_list(method1, method2)
        if not methods:
            print("At least one authorization method is required")
            return 1

        path = aaa_path("authorization/config")
        body = {
            "openconfig-system:config": {
                "authorization-method": methods
            }
        }
        resp = ApiClient().patch(path, body)
        return check_ok(resp)

    @staticmethod
    def delete_openconfig_aaa_aaa_authorization_login(*args):
        """Delete authorization login methods (reset to default)."""
        path = aaa_path("authorization/config/authorization-method")
        resp = ApiClient().delete(path)
        return check_ok(resp)

    @staticmethod
    def patch_openconfig_aaa_aaa_accounting_login(method1, method2=None, *args):
        """Set accounting login methods."""
        if method1 == "disable":
            return Handlers.delete_openconfig_aaa_aaa_accounting_login()

        methods = methods_to_list(method1, method2)
        if not methods:
            print("At least one accounting method is required")
            return 1

        path = aaa_path("accounting/config")
        body = {
            "openconfig-system:config": {
                "accounting-method": methods
            }
        }
        resp = ApiClient().patch(path, body)
        return check_ok(resp)

    @staticmethod
    def delete_openconfig_aaa_aaa_accounting_login(*args):
        """Delete accounting login methods (reset to default/disable)."""
        path = aaa_path("accounting/config/accounting-method")
        resp = ApiClient().delete(path)
        return check_ok(resp)

    @staticmethod
    def get_openconfig_aaa_aaa(template, *args):
        """Get all AAA configuration and display using template."""
        resp = ApiClient().get(AAA_PATH, ignore404=True)
        if not resp.ok():
            print(resp.error_message())
            return 1

        aaa_data = {
            "authentication": {
                "login": "local (default)",
                "failthrough": "False (default)",
                "fallback": "False (default)",
                "debug": "False (default)",
                "trace": "False (default)"
            },
            "authorization": {
                "login": "local (default)"
            },
            "accounting": {
                "login": "disable (default)"
            }
        }

        if resp.content:
            data = resp.content.get("openconfig-system:aaa", {})

            # Parse authentication config
            auth_config = data.get("authentication", {}).get("config", {})
            if "authentication-method" in auth_config:
                methods = auth_config["authentication-method"]
                if methods:
                    aaa_data["authentication"]["login"] = ",".join(methods)

            if "openconfig-system-ext:failthrough" in auth_config:
                aaa_data["authentication"]["failthrough"] = str(auth_config["openconfig-system-ext:failthrough"])

            if "openconfig-system-ext:fallback" in auth_config:
                aaa_data["authentication"]["fallback"] = str(auth_config["openconfig-system-ext:fallback"])

            if "openconfig-system-ext:debug" in auth_config:
                aaa_data["authentication"]["debug"] = str(auth_config["openconfig-system-ext:debug"])

            if "openconfig-system-ext:trace" in auth_config:
                aaa_data["authentication"]["trace"] = str(auth_config["openconfig-system-ext:trace"])

            # Parse authorization config
            authz_config = data.get("authorization", {}).get("config", {})
            if "authorization-method" in authz_config:
                methods = authz_config["authorization-method"]
                if methods:
                    aaa_data["authorization"]["login"] = ",".join(methods)

            # Parse accounting config
            acct_config = data.get("accounting", {}).get("config", {})
            if "accounting-method" in acct_config:
                methods = acct_config["accounting-method"]
                if methods:
                    aaa_data["accounting"]["login"] = ",".join(methods)

        show_cli_output(template, aaa_data)
        return 0


def run(func, args):
    """Entry point for CLI actioner."""
    return getattr(Handlers, func)(*args)


if __name__ == '__main__':
    pipestr().write(sys.argv)
    func = sys.argv[1]
    run(func, sys.argv[2:])
