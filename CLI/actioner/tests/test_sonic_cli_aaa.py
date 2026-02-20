#!/usr/bin/python3
import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.modules["rpipe_utils"] = Mock()
sys.modules["scripts"] = Mock()
sys.modules["scripts.render_cli"] = Mock()

mock_cc = Mock()
mock_path_cls = Mock()
mock_api_client_cls = Mock()
mock_cc.Path = mock_path_cls
mock_cc.ApiClient = mock_api_client_cls
sys.modules["cli_client"] = mock_cc

import sonic_cli_aaa


class TestBoolFromOption:
    def test_enable(self):
        assert sonic_cli_aaa.bool_from_option("enable") is True

    def test_disable(self):
        assert sonic_cli_aaa.bool_from_option("disable") is False

    def test_default(self):
        assert sonic_cli_aaa.bool_from_option("default") is False

    def test_unknown(self):
        assert sonic_cli_aaa.bool_from_option("unknown") is False


class TestCheckResponse:
    def test_ok_response(self):
        resp = Mock()
        resp.ok.return_value = True
        assert sonic_cli_aaa.check_response(resp) == 0

    def test_error_response(self):
        resp = Mock()
        resp.ok.return_value = False
        resp.error_message.return_value = "Error occurred"
        assert sonic_cli_aaa.check_response(resp) == 1


class TestInvokeFailthrough:
    def setup_method(self):
        mock_api_client_cls.reset_mock()
        mock_path_cls.reset_mock()

    def test_patch_failthrough_enable(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_authentication_config_failthrough",
            ["enable"],
        )
        mock_api.patch.assert_called_once()
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:failthrough"] is True

    def test_patch_failthrough_disable(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_authentication_config_failthrough",
            ["disable"],
        )
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:failthrough"] is False

    def test_delete_failthrough(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.delete.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "delete_openconfig_aaa_aaa_authentication_config_failthrough",
            [],
        )
        mock_api.delete.assert_called_once()


class TestInvokeFallback:
    def setup_method(self):
        mock_api_client_cls.reset_mock()
        mock_path_cls.reset_mock()

    def test_patch_fallback_enable(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_authentication_config_fallback",
            ["enable"],
        )
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:fallback"] is True

    def test_delete_fallback(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.delete.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "delete_openconfig_aaa_aaa_authentication_config_fallback",
            [],
        )
        mock_api.delete.assert_called_once()


class TestInvokeDebug:
    def setup_method(self):
        mock_api_client_cls.reset_mock()
        mock_path_cls.reset_mock()

    def test_patch_debug_enable(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_authentication_config_debug",
            ["enable"],
        )
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:debug"] is True

    def test_delete_debug(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.delete.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "delete_openconfig_aaa_aaa_authentication_config_debug",
            [],
        )
        mock_api.delete.assert_called_once()


class TestInvokeAuthenticationMethod:
    def setup_method(self):
        mock_api_client_cls.reset_mock()
        mock_path_cls.reset_mock()

    def test_patch_single_method(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_authentication_config_authentication_method",
            ["tacacs+"],
        )
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:authentication-method"] == ["tacacs+"]

    def test_patch_multiple_methods(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_authentication_config_authentication_method",
            ["tacacs+", "local"],
        )
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:authentication-method"] == ["tacacs+", "local"]

    def test_patch_methods_filters_empty(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_authentication_config_authentication_method",
            ["tacacs+", "", "local", "  "],
        )
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:authentication-method"] == ["tacacs+", "local"]

    def test_delete_authentication_method(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.delete.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "delete_openconfig_aaa_aaa_authentication_config_authentication_method",
            [],
        )
        mock_api.delete.assert_called_once()


class TestInvokeAuthorization:
    def setup_method(self):
        mock_api_client_cls.reset_mock()
        mock_path_cls.reset_mock()

    def test_patch_authorization_method(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_authorization_config_authorization_method",
            ["tacacs+"],
        )
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:authorization-method"] == ["tacacs+"]

    def test_delete_authorization_method(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.delete.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "delete_openconfig_aaa_aaa_authorization_config_authorization_method",
            [],
        )
        mock_api.delete.assert_called_once()


class TestInvokeAccounting:
    def setup_method(self):
        mock_api_client_cls.reset_mock()
        mock_path_cls.reset_mock()

    def test_patch_accounting_method(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "patch_openconfig_aaa_aaa_accounting_config_accounting_method",
            ["tacacs+"],
        )
        call_args = mock_api.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-aaa:accounting-method"] == ["tacacs+"]

    def test_delete_accounting_method(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.delete.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "delete_openconfig_aaa_aaa_accounting_config_accounting_method",
            [],
        )
        mock_api.delete.assert_called_once()


class TestInvokeGetAAA:
    def setup_method(self):
        mock_api_client_cls.reset_mock()
        mock_path_cls.reset_mock()

    @patch("sonic_cli_aaa.show_cli_output")
    def test_get_aaa_success(self, mock_show):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_resp.content = {
            "openconfig-aaa:aaa": {
                "authentication": {
                    "config": {"authentication-method": ["local"]}
                }
            }
        }
        mock_api.get.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "get_openconfig_aaa_aaa",
            ["show_aaa.j2"],
        )
        mock_show.assert_called_once()

    def test_get_aaa_error(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = False
        mock_resp.error_message.return_value = "Not found"
        mock_api.get.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "get_openconfig_aaa_aaa",
            ["show_aaa.j2"],
        )
        assert result == mock_resp

    @patch("sonic_cli_aaa.show_cli_output")
    def test_get_aaa_empty_content(self, mock_show):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_resp.content = None
        mock_api.get.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        result = sonic_cli_aaa.invoke(
            "get_openconfig_aaa_aaa",
            ["show_aaa.j2"],
        )
        mock_show.assert_not_called()


class TestInvokeUnimplemented:
    def test_unknown_function(self, capsys):
        result = sonic_cli_aaa.invoke("unknown_function", [])
        captured = capsys.readouterr()
        assert "%Error: not implemented" in captured.out
        assert result is None


class TestRun:
    def setup_method(self):
        mock_api_client_cls.reset_mock()
        mock_path_cls.reset_mock()

    def test_run_calls_invoke_and_check(self):
        mock_api = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_api.patch.return_value = mock_resp
        mock_api_client_cls.return_value = mock_api

        sonic_cli_aaa.run(
            "patch_openconfig_aaa_aaa_authentication_config_failthrough",
            ["enable"],
        )
        mock_api.patch.assert_called_once()

    def test_run_handles_none_response(self):
        sonic_cli_aaa.run("unknown_function", [])


class TestConstants:
    def test_aaa_path(self):
        assert sonic_cli_aaa.AAA_PATH == "/restconf/data/openconfig-aaa:aaa"

    def test_authentication_path(self):
        assert "authentication" in sonic_cli_aaa.AAA_AUTHENTICATION_PATH

    def test_authorization_path(self):
        assert "authorization" in sonic_cli_aaa.AAA_AUTHORIZATION_PATH

    def test_accounting_path(self):
        assert "accounting" in sonic_cli_aaa.AAA_ACCOUNTING_PATH
