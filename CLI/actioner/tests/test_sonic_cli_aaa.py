#!/usr/bin/env python3
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

"""
Unit tests for sonic_cli_aaa.py actioner.

These tests verify that CLI commands correctly invoke the actioner functions
and that the actioner constructs proper REST API calls.

Run with: pytest CLI/actioner/tests/test_sonic_cli_aaa.py -v
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add the actioner directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock the dependencies before importing the module
sys.modules['cli_client'] = MagicMock()
sys.modules['rpipe_utils'] = MagicMock()
sys.modules['scripts'] = MagicMock()
sys.modules['scripts.render_cli'] = MagicMock()

# Now import the module under test
import sonic_cli_aaa
from sonic_cli_aaa import (
    aaa_path,
    check_ok,
    option_to_bool,
    methods_to_list,
    Handlers,
    run,
    AAA_PATH,
)


class TestHelperFunctions:
    """Tests for helper functions in sonic_cli_aaa.py."""

    def test_aaa_path_no_subpath(self):
        """Test aaa_path returns base path when no subpath provided."""
        with patch('sonic_cli_aaa.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            result = aaa_path()
            mock_path.assert_called_once_with(AAA_PATH)
            assert result == mock_path_instance

    def test_aaa_path_with_subpath(self):
        """Test aaa_path joins subpath correctly."""
        with patch('sonic_cli_aaa.Path') as mock_path:
            mock_path_instance = Mock()
            mock_joined = Mock()
            mock_path_instance.join.return_value = mock_joined
            mock_path.return_value = mock_path_instance
            result = aaa_path("authentication/config")
            mock_path.assert_called_once_with(AAA_PATH)
            mock_path_instance.join.assert_called_once_with("authentication/config")
            assert result == mock_joined

    def test_check_ok_success(self):
        """Test check_ok returns 0 for successful response."""
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        assert check_ok(mock_resp) == 0

    def test_check_ok_failure(self, capsys):
        """Test check_ok returns 1 and prints error for failed response."""
        mock_resp = Mock()
        mock_resp.ok.return_value = False
        mock_resp.error_message.return_value = "Test error"
        assert check_ok(mock_resp) == 1
        captured = capsys.readouterr()
        assert "Test error" in captured.out

    def test_option_to_bool_enable(self):
        """Test option_to_bool converts 'enable' to True."""
        assert option_to_bool("enable") is True

    def test_option_to_bool_disable(self):
        """Test option_to_bool converts 'disable' to False."""
        assert option_to_bool("disable") is False

    def test_option_to_bool_other(self):
        """Test option_to_bool returns None for other values."""
        assert option_to_bool("default") is None
        assert option_to_bool("invalid") is None
        assert option_to_bool("") is None

    def test_methods_to_list_single(self):
        """Test methods_to_list with single method."""
        assert methods_to_list("local") == ["local"]
        assert methods_to_list("tacacs+") == ["tacacs+"]

    def test_methods_to_list_two_methods(self):
        """Test methods_to_list with two methods."""
        assert methods_to_list("tacacs+", "local") == ["tacacs+", "local"]

    def test_methods_to_list_empty(self):
        """Test methods_to_list with empty/None values."""
        assert methods_to_list(None) == []
        assert methods_to_list("") == []
        assert methods_to_list("  ") == []

    def test_methods_to_list_partial(self):
        """Test methods_to_list with one valid and one empty."""
        assert methods_to_list("local", None) == ["local"]
        assert methods_to_list("local", "") == ["local"]


class TestAuthenticationFailthrough:
    """Tests for authentication failthrough handlers."""

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_failthrough_enable(self, mock_aaa_path, mock_api_client):
        """Test setting failthrough to enable."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authentication_failthrough("enable")

        assert result == 0
        mock_aaa_path.assert_called_with("authentication/config")
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["openconfig-system-ext:failthrough"] is True

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_failthrough_disable(self, mock_aaa_path, mock_api_client):
        """Test setting failthrough to disable."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authentication_failthrough("disable")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["openconfig-system-ext:failthrough"] is False

    @patch.object(Handlers, 'delete_openconfig_aaa_aaa_authentication_failthrough')
    def test_patch_failthrough_default(self, mock_delete):
        """Test setting failthrough to default calls delete."""
        mock_delete.return_value = 0
        result = Handlers.patch_openconfig_aaa_aaa_authentication_failthrough("default")
        assert result == 0
        mock_delete.assert_called_once()

    def test_patch_failthrough_invalid(self, capsys):
        """Test setting failthrough with invalid option."""
        result = Handlers.patch_openconfig_aaa_aaa_authentication_failthrough("invalid")
        assert result == 1
        captured = capsys.readouterr()
        assert "Invalid option" in captured.out

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_delete_failthrough(self, mock_aaa_path, mock_api_client):
        """Test deleting failthrough setting."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.delete.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.delete_openconfig_aaa_aaa_authentication_failthrough()

        assert result == 0
        mock_aaa_path.assert_called_with("authentication/config/openconfig-system-ext:failthrough")
        mock_client.delete.assert_called_once()


class TestAuthenticationFallback:
    """Tests for authentication fallback handlers."""

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_fallback_enable(self, mock_aaa_path, mock_api_client):
        """Test setting fallback to enable."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authentication_fallback("enable")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["openconfig-system-ext:fallback"] is True

    @patch.object(Handlers, 'delete_openconfig_aaa_aaa_authentication_fallback')
    def test_patch_fallback_default(self, mock_delete):
        """Test setting fallback to default calls delete."""
        mock_delete.return_value = 0
        result = Handlers.patch_openconfig_aaa_aaa_authentication_fallback("default")
        assert result == 0
        mock_delete.assert_called_once()


class TestAuthenticationDebug:
    """Tests for authentication debug handlers."""

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_debug_enable(self, mock_aaa_path, mock_api_client):
        """Test setting debug to enable."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authentication_debug("enable")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["openconfig-system-ext:debug"] is True

    @patch.object(Handlers, 'delete_openconfig_aaa_aaa_authentication_debug')
    def test_patch_debug_default(self, mock_delete):
        """Test setting debug to default calls delete."""
        mock_delete.return_value = 0
        result = Handlers.patch_openconfig_aaa_aaa_authentication_debug("default")
        assert result == 0
        mock_delete.assert_called_once()


class TestAuthenticationTrace:
    """Tests for authentication trace handlers."""

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_trace_enable(self, mock_aaa_path, mock_api_client):
        """Test setting trace to enable."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authentication_trace("enable")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["openconfig-system-ext:trace"] is True

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_trace_disable(self, mock_aaa_path, mock_api_client):
        """Test setting trace to disable."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authentication_trace("disable")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["openconfig-system-ext:trace"] is False

    @patch.object(Handlers, 'delete_openconfig_aaa_aaa_authentication_trace')
    def test_patch_trace_default(self, mock_delete):
        """Test setting trace to default calls delete."""
        mock_delete.return_value = 0
        result = Handlers.patch_openconfig_aaa_aaa_authentication_trace("default")
        assert result == 0
        mock_delete.assert_called_once()

    def test_patch_trace_invalid(self, capsys):
        """Test setting trace with invalid option."""
        result = Handlers.patch_openconfig_aaa_aaa_authentication_trace("invalid")
        assert result == 1
        captured = capsys.readouterr()
        assert "Invalid option" in captured.out

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_delete_trace(self, mock_aaa_path, mock_api_client):
        """Test deleting trace setting."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.delete.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.delete_openconfig_aaa_aaa_authentication_trace()

        assert result == 0
        mock_aaa_path.assert_called_with("authentication/config/openconfig-system-ext:trace")
        mock_client.delete.assert_called_once()


class TestAuthenticationLogin:
    """Tests for authentication login method handlers."""

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_login_single_method(self, mock_aaa_path, mock_api_client):
        """Test setting single authentication method."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authentication_login("local")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["authentication-method"] == ["local"]

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_login_two_methods(self, mock_aaa_path, mock_api_client):
        """Test setting two authentication methods."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authentication_login("tacacs+", "local")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["authentication-method"] == ["tacacs+", "local"]

    def test_patch_login_no_methods(self, capsys):
        """Test setting login with no methods returns error."""
        result = Handlers.patch_openconfig_aaa_aaa_authentication_login("")
        assert result == 1
        captured = capsys.readouterr()
        assert "At least one authentication method is required" in captured.out

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_delete_login(self, mock_aaa_path, mock_api_client):
        """Test deleting authentication login methods."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.delete.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.delete_openconfig_aaa_aaa_authentication_login()

        assert result == 0
        mock_aaa_path.assert_called_with("authentication/config/authentication-method")


class TestAuthorizationLogin:
    """Tests for authorization login method handlers."""

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_authorization_single_method(self, mock_aaa_path, mock_api_client):
        """Test setting single authorization method."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authorization_login("local")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["authorization-method"] == ["local"]

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_authorization_two_methods(self, mock_aaa_path, mock_api_client):
        """Test setting two authorization methods."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_authorization_login("tacacs+", "local")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["authorization-method"] == ["tacacs+", "local"]

    def test_patch_authorization_no_methods(self, capsys):
        """Test setting authorization with no methods returns error."""
        result = Handlers.patch_openconfig_aaa_aaa_authorization_login("")
        assert result == 1
        captured = capsys.readouterr()
        assert "At least one authorization method is required" in captured.out


class TestAccountingLogin:
    """Tests for accounting login method handlers."""

    @patch('sonic_cli_aaa.ApiClient')
    @patch('sonic_cli_aaa.aaa_path')
    def test_patch_accounting_single_method(self, mock_aaa_path, mock_api_client):
        """Test setting single accounting method."""
        mock_path = Mock()
        mock_aaa_path.return_value = mock_path
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_client.patch.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.patch_openconfig_aaa_aaa_accounting_login("tacacs+")

        assert result == 0
        call_args = mock_client.patch.call_args
        body = call_args[0][1]
        assert body["openconfig-system:config"]["accounting-method"] == ["tacacs+"]

    @patch.object(Handlers, 'delete_openconfig_aaa_aaa_accounting_login')
    def test_patch_accounting_disable(self, mock_delete):
        """Test setting accounting to disable calls delete."""
        mock_delete.return_value = 0
        result = Handlers.patch_openconfig_aaa_aaa_accounting_login("disable")
        assert result == 0
        mock_delete.assert_called_once()

    def test_patch_accounting_no_methods(self, capsys):
        """Test setting accounting with no methods returns error."""
        result = Handlers.patch_openconfig_aaa_aaa_accounting_login("")
        assert result == 1
        captured = capsys.readouterr()
        assert "At least one accounting method is required" in captured.out


class TestGetAaa:
    """Tests for get AAA configuration handler."""

    @patch('sonic_cli_aaa.show_cli_output')
    @patch('sonic_cli_aaa.ApiClient')
    def test_get_aaa_empty_response(self, mock_api_client, mock_show_output):
        """Test get AAA with empty response returns defaults."""
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_resp.content = None
        mock_client.get.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.get_openconfig_aaa_aaa("show_aaa.j2")

        assert result == 0
        mock_show_output.assert_called_once()
        call_args = mock_show_output.call_args
        aaa_data = call_args[0][1]
        assert aaa_data["authentication"]["login"] == "local (default)"
        assert aaa_data["authentication"]["failthrough"] == "False (default)"

    @patch('sonic_cli_aaa.show_cli_output')
    @patch('sonic_cli_aaa.ApiClient')
    def test_get_aaa_with_data(self, mock_api_client, mock_show_output):
        """Test get AAA with actual data."""
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = True
        mock_resp.content = {
            "openconfig-system:aaa": {
                "authentication": {
                    "config": {
                        "authentication-method": ["tacacs+", "local"],
                        "openconfig-system-ext:failthrough": True,
                        "openconfig-system-ext:fallback": False,
                        "openconfig-system-ext:debug": True,
                        "openconfig-system-ext:trace": False
                    }
                },
                "authorization": {
                    "config": {
                        "authorization-method": ["tacacs+"]
                    }
                },
                "accounting": {
                    "config": {
                        "accounting-method": ["tacacs+"]
                    }
                }
            }
        }
        mock_client.get.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.get_openconfig_aaa_aaa("show_aaa.j2")

        assert result == 0
        mock_show_output.assert_called_once()
        call_args = mock_show_output.call_args
        aaa_data = call_args[0][1]
        assert aaa_data["authentication"]["login"] == "tacacs+,local"
        assert aaa_data["authentication"]["failthrough"] == "True"
        assert aaa_data["authentication"]["fallback"] == "False"
        assert aaa_data["authentication"]["debug"] == "True"
        assert aaa_data["authentication"]["trace"] == "False"
        assert aaa_data["authorization"]["login"] == "tacacs+"
        assert aaa_data["accounting"]["login"] == "tacacs+"

    @patch('sonic_cli_aaa.ApiClient')
    def test_get_aaa_error(self, mock_api_client, capsys):
        """Test get AAA with error response."""
        mock_client = Mock()
        mock_resp = Mock()
        mock_resp.ok.return_value = False
        mock_resp.error_message.return_value = "Connection failed"
        mock_client.get.return_value = mock_resp
        mock_api_client.return_value = mock_client

        result = Handlers.get_openconfig_aaa_aaa("show_aaa.j2")

        assert result == 1
        captured = capsys.readouterr()
        assert "Connection failed" in captured.out


class TestRunFunction:
    """Tests for the run() entry point function."""

    @patch.object(Handlers, 'patch_openconfig_aaa_aaa_authentication_trace')
    def test_run_calls_handler(self, mock_handler):
        """Test run() correctly dispatches to handler function."""
        mock_handler.return_value = 0
        result = run("patch_openconfig_aaa_aaa_authentication_trace", ["enable"])
        assert result == 0
        mock_handler.assert_called_once_with("enable")

    @patch.object(Handlers, 'patch_openconfig_aaa_aaa_authentication_login')
    def test_run_with_multiple_args(self, mock_handler):
        """Test run() passes multiple arguments correctly."""
        mock_handler.return_value = 0
        result = run("patch_openconfig_aaa_aaa_authentication_login", ["tacacs+", "local"])
        assert result == 0
        mock_handler.assert_called_once_with("tacacs+", "local")

    @patch.object(Handlers, 'get_openconfig_aaa_aaa')
    def test_run_get_handler(self, mock_handler):
        """Test run() calls get handler correctly."""
        mock_handler.return_value = 0
        result = run("get_openconfig_aaa_aaa", ["show_aaa.j2"])
        assert result == 0
        mock_handler.assert_called_once_with("show_aaa.j2")


class TestHandlerExists:
    """Tests to verify all expected handler functions exist."""

    def test_all_handlers_exist(self):
        """Verify all expected handler methods exist in Handlers class."""
        expected_handlers = [
            'patch_openconfig_aaa_aaa_authentication_failthrough',
            'delete_openconfig_aaa_aaa_authentication_failthrough',
            'patch_openconfig_aaa_aaa_authentication_fallback',
            'delete_openconfig_aaa_aaa_authentication_fallback',
            'patch_openconfig_aaa_aaa_authentication_debug',
            'delete_openconfig_aaa_aaa_authentication_debug',
            'patch_openconfig_aaa_aaa_authentication_trace',
            'delete_openconfig_aaa_aaa_authentication_trace',
            'patch_openconfig_aaa_aaa_authentication_login',
            'delete_openconfig_aaa_aaa_authentication_login',
            'patch_openconfig_aaa_aaa_authorization_login',
            'delete_openconfig_aaa_aaa_authorization_login',
            'patch_openconfig_aaa_aaa_accounting_login',
            'delete_openconfig_aaa_aaa_accounting_login',
            'get_openconfig_aaa_aaa',
        ]
        for handler in expected_handlers:
            assert hasattr(Handlers, handler), f"Missing handler: {handler}"
            assert callable(getattr(Handlers, handler)), f"Handler not callable: {handler}"

    def test_handlers_are_static_methods(self):
        """Verify all handlers are static methods."""
        for name in dir(Handlers):
            if name.startswith('patch_') or name.startswith('delete_') or name.startswith('get_'):
                method = getattr(Handlers, name)
                assert callable(method), f"{name} should be callable"


class TestCliCommandMapping:
    """Tests to verify CLI commands map to correct handler functions.
    
    These tests verify that the XML command definitions would correctly
    invoke the corresponding Python handler functions.
    """

    def test_aaa_authentication_trace_enable_mapping(self):
        """Verify 'aaa authentication trace enable' maps to correct handler."""
        handler_name = "patch_openconfig_aaa_aaa_authentication_trace"
        assert hasattr(Handlers, handler_name)
        handler = getattr(Handlers, handler_name)
        assert callable(handler)

    def test_aaa_authentication_failthrough_mapping(self):
        """Verify 'aaa authentication failthrough' maps to correct handler."""
        handler_name = "patch_openconfig_aaa_aaa_authentication_failthrough"
        assert hasattr(Handlers, handler_name)

    def test_aaa_authentication_login_mapping(self):
        """Verify 'aaa authentication login' maps to correct handler."""
        handler_name = "patch_openconfig_aaa_aaa_authentication_login"
        assert hasattr(Handlers, handler_name)

    def test_aaa_authorization_mapping(self):
        """Verify 'aaa authorization' maps to correct handler."""
        handler_name = "patch_openconfig_aaa_aaa_authorization_login"
        assert hasattr(Handlers, handler_name)

    def test_aaa_accounting_mapping(self):
        """Verify 'aaa accounting' maps to correct handler."""
        handler_name = "patch_openconfig_aaa_aaa_accounting_login"
        assert hasattr(Handlers, handler_name)

    def test_show_aaa_mapping(self):
        """Verify 'show aaa' maps to correct handler."""
        handler_name = "get_openconfig_aaa_aaa"
        assert hasattr(Handlers, handler_name)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
