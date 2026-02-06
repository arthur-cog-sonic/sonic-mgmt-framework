# AAA Klish CLI High-Level Design Document

## 1. Overview

This document describes the design and implementation of Klish-based AAA (Authentication, Authorization, and Accounting) CLI commands for SONiC. The implementation migrates existing Click-based AAA commands from `sonic-utilities` to the Klish framework in `sonic-mgmt-framework`, using the three-layer architecture (XML definitions, Python actioners, Jinja2 templates) and OpenConfig to SONiC YANG model transformation.

## 2. Architecture

### 2.1 Three-Layer Klish Architecture

The Klish CLI framework uses a three-layer architecture:

1. **XML Command Definitions** (`CLI/clitree/cli-xml/aaa.xml`): Define command syntax, parameters, help text, and action bindings.

2. **Python Actioners** (`CLI/actioner/sonic-cli-aaa.py`): Execute REST API calls to the management framework backend and process responses.

3. **Jinja2 Templates** (`CLI/renderer/templates/show_aaa.j2`): Format command output for display to the user.

### 2.2 OpenConfig to SONiC Transformation

The transformation layer bridges the gap between OpenConfig YANG models and SONiC's native Redis-based configuration:

```
CLI Command
    |
    v
Python Actioner (REST API call)
    |
    v
REST Server (sonic-mgmt-framework)
    |
    v
Translib (sonic-mgmt-common)
    |
    v
Transformer (xfmr_aaa.go)
    |
    v
ConfigDB (Redis)
```

### 2.3 Data Model Mapping

**OpenConfig AAA Model** (`openconfig-system:system/aaa`):
- Hierarchical structure with separate containers for authentication, authorization, and accounting
- Uses `leaf-list authentication-method` for ordered list of methods
- Boolean fields for failthrough, fallback, debug, trace

**SONiC Native AAA Model** (`sonic-system-aaa`):
- Flat Redis table structure: `AAA|authentication`, `AAA|authorization`, `AAA|accounting`
- Uses `login` field with comma-separated string pattern
- Boolean fields stored as "True"/"False" strings

## 3. Component Design

### 3.1 XML Command Definitions (aaa.xml)

The XML file defines the following commands:

**Configuration Commands:**
- `aaa authentication failthrough {enable|disable|default}` - Set authentication failthrough behavior
- `aaa authentication fallback {enable|disable|default}` - Set authentication fallback behavior
- `aaa authentication debug {enable|disable|default}` - Enable/disable debug mode
- `aaa authentication trace {enable|disable|default}` - Enable/disable trace mode
- `aaa authentication login <method1> [method2]` - Set authentication methods
- `aaa authorization login <method1> [method2]` - Set authorization methods
- `aaa accounting login <method1> [method2]` - Set accounting methods

**Negation Commands:**
- `no aaa authentication failthrough` - Reset failthrough to default
- `no aaa authentication fallback` - Reset fallback to default
- `no aaa authentication debug` - Reset debug to default
- `no aaa authentication trace` - Reset trace to default
- `no aaa authentication login` - Reset authentication methods to default
- `no aaa authorization login` - Reset authorization methods to default
- `no aaa accounting login` - Reset accounting methods to default

**Show Commands:**
- `show aaa` - Display all AAA configuration

### 3.2 Python Actioner (sonic-cli-aaa.py)

The actioner implements the `Handlers` class with static methods for each operation:

**Configuration Methods:**
- `patch_openconfig_aaa_aaa_authentication_failthrough(option)` - PATCH failthrough setting
- `patch_openconfig_aaa_aaa_authentication_fallback(option)` - PATCH fallback setting
- `patch_openconfig_aaa_aaa_authentication_debug(option)` - PATCH debug setting
- `patch_openconfig_aaa_aaa_authentication_trace(option)` - PATCH trace setting
- `patch_openconfig_aaa_aaa_authentication_login(method1, method2)` - PATCH authentication methods
- `patch_openconfig_aaa_aaa_authorization_login(method1, method2)` - PATCH authorization methods
- `patch_openconfig_aaa_aaa_accounting_login(method1, method2)` - PATCH accounting methods

**Delete Methods:**
- `delete_openconfig_aaa_aaa_authentication_failthrough()` - DELETE failthrough
- `delete_openconfig_aaa_aaa_authentication_fallback()` - DELETE fallback
- `delete_openconfig_aaa_aaa_authentication_debug()` - DELETE debug
- `delete_openconfig_aaa_aaa_authentication_trace()` - DELETE trace
- `delete_openconfig_aaa_aaa_authentication_login()` - DELETE authentication methods
- `delete_openconfig_aaa_aaa_authorization_login()` - DELETE authorization methods
- `delete_openconfig_aaa_aaa_accounting_login()` - DELETE accounting methods

**Query Methods:**
- `get_openconfig_aaa_aaa(template)` - GET all AAA configuration

### 3.3 Jinja2 Template (show_aaa.j2)

The template formats the AAA configuration output:

```
AAA authentication login <methods>
AAA authentication failthrough <True/False>
AAA authentication fallback <True/False>
AAA authentication debug <True/False>
AAA authentication trace <True/False>
AAA authorization login <methods>
AAA accounting login <methods>
```

### 3.4 YANG Annotations (openconfig-aaa-annot.yang)

The annotation file maps OpenConfig paths to transformer functions:

- `/oc-sys:system/oc-sys:aaa` - `sonic-ext:subtree-transformer "aaa_subtree_xfmr"`
- `/oc-sys:system/oc-sys:aaa/oc-sys:authentication` - `sonic-ext:table-name "AAA"`, `sonic-ext:key-transformer "aaa_authentication_key_xfmr"`
- `/oc-sys:system/oc-sys:aaa/oc-sys:authentication/oc-sys:config/oc-sys:authentication-method` - `sonic-ext:field-transformer "aaa_auth_method_xfmr"`

Similar annotations for authorization and accounting containers.

### 3.5 Go Transformer (xfmr_aaa.go)

The transformer implements bidirectional conversion:

**YangToDb Transformers:**
- `YangToDb_aaa_subtree_xfmr` - Handles entire AAA subtree for writes
- `YangToDb_aaa_auth_method_xfmr` - Converts authentication-method list to login string
- `YangToDb_aaa_authz_method_xfmr` - Converts authorization-method list to login string
- `YangToDb_aaa_acct_method_xfmr` - Converts accounting-method list to login string

**DbToYang Transformers:**
- `DbToYang_aaa_subtree_xfmr` - Reads AAA table and populates OpenConfig structure
- `DbToYang_aaa_auth_method_xfmr` - Converts login string to authentication-method list
- `DbToYang_aaa_authz_method_xfmr` - Converts login string to authorization-method list
- `DbToYang_aaa_acct_method_xfmr` - Converts login string to accounting-method list

**Key Transformers:**
- `aaa_authentication_key_xfmr` - Returns "authentication" key
- `aaa_authorization_key_xfmr` - Returns "authorization" key
- `aaa_accounting_key_xfmr` - Returns "accounting" key

## 4. Command Mapping Table

| Click Command | Klish Command | OpenConfig Path | SONiC Table |
|--------------|---------------|-----------------|-------------|
| `config aaa authentication failthrough enable` | `aaa authentication failthrough enable` | `/openconfig-system:system/aaa/authentication/config/failthrough` | `AAA\|authentication\|failthrough` |
| `config aaa authentication failthrough disable` | `aaa authentication failthrough disable` | `/openconfig-system:system/aaa/authentication/config/failthrough` | `AAA\|authentication\|failthrough` |
| `config aaa authentication failthrough default` | `aaa authentication failthrough default` | DELETE `/openconfig-system:system/aaa/authentication/config/failthrough` | `AAA\|authentication\|failthrough` |
| `config aaa authentication fallback enable` | `aaa authentication fallback enable` | `/openconfig-system:system/aaa/authentication/config/fallback` | `AAA\|authentication\|fallback` |
| `config aaa authentication debug enable` | `aaa authentication debug enable` | `/openconfig-system:system/aaa/authentication/config/debug` | `AAA\|authentication\|debug` |
| `config aaa authentication login tacacs+ local` | `aaa authentication login tacacs+ local` | `/openconfig-system:system/aaa/authentication/config/authentication-method` | `AAA\|authentication\|login` |
| `config aaa authorization login tacacs+` | `aaa authorization login tacacs+` | `/openconfig-system:system/aaa/authorization/config/authorization-method` | `AAA\|authorization\|login` |
| `config aaa accounting login tacacs+` | `aaa accounting login tacacs+` | `/openconfig-system:system/aaa/accounting/config/accounting-method` | `AAA\|accounting\|login` |
| `show aaa` | `show aaa` | GET `/openconfig-system:system/aaa` | `AAA` table |

## 5. Transformer Design Details

### 5.1 Authentication Method Transformation

**OpenConfig Format:**
```json
{
  "authentication-method": ["TACACS_ALL", "LOCAL"]
}
```

**SONiC Format:**
```
login: "tacacs+,local"
```

**Transformation Logic:**
- YangToDb: Join list elements with comma, convert identityref to string (TACACS_ALL -> "tacacs+", LOCAL -> "local", RADIUS_ALL -> "radius")
- DbToYang: Split comma-separated string, convert strings to identityref

### 5.2 Boolean Field Transformation

**OpenConfig Format:**
```json
{
  "failthrough": true
}
```

**SONiC Format:**
```
failthrough: "True"
```

**Transformation Logic:**
- YangToDb: Convert Go boolean to "True"/"False" string
- DbToYang: Convert "True"/"False" string to Go boolean

### 5.3 Key Transformation

OpenConfig uses separate containers for authentication, authorization, and accounting. SONiC uses a single AAA table with type-based keys.

**Key Mapping:**
- `/aaa/authentication` -> `AAA|authentication`
- `/aaa/authorization` -> `AAA|authorization`
- `/aaa/accounting` -> `AAA|accounting`

## 6. Example Workflows

### 6.1 Configuration Command Flow

**Command:** `aaa authentication login tacacs+ local`

1. **CLI Parsing:** KLISH parses command, extracts parameters `method1=tacacs+`, `method2=local`
2. **Actioner Call:** `sonic_cli_aaa patch_openconfig_aaa_aaa_authentication_login tacacs+ local`
3. **REST API:** PATCH `/restconf/data/openconfig-system:system/aaa/authentication/config`
   ```json
   {
     "openconfig-system:config": {
       "authentication-method": ["tacacs+", "local"]
     }
   }
   ```
4. **Translib:** Receives request, invokes transformer
5. **Transformer:** `YangToDb_aaa_subtree_xfmr` converts to Redis format
6. **CVL Validation:** Validates against YANG schema
7. **ConfigDB Write:** Sets `AAA|authentication` with `login: "tacacs+,local"`

### 6.2 Show Command Flow

**Command:** `show aaa`

1. **CLI Parsing:** KLISH parses command
2. **Actioner Call:** `sonic_cli_aaa get_openconfig_aaa_aaa show_aaa.j2`
3. **REST API:** GET `/restconf/data/openconfig-system:system/aaa`
4. **Translib:** Receives request, invokes transformer
5. **Transformer:** `DbToYang_aaa_subtree_xfmr` reads from Redis, converts to OpenConfig
6. **Response:** Returns JSON with AAA configuration
7. **Actioner:** Processes response, extracts relevant fields
8. **Template:** `show_aaa.j2` formats output
9. **Display:** Shows formatted AAA configuration to user

## 7. Files Created

| File | Location | Purpose |
|------|----------|---------|
| `aaa.xml` | `sonic-mgmt-framework/CLI/clitree/cli-xml/` | XML command definitions |
| `sonic-cli-aaa.py` | `sonic-mgmt-framework/CLI/actioner/` | Python actioner |
| `show_aaa.j2` | `sonic-mgmt-framework/CLI/renderer/templates/` | Jinja2 output template |
| `openconfig-aaa-annot.yang` | `sonic-mgmt-common/models/yang/annotations/` | YANG annotations |
| `xfmr_aaa.go` | `sonic-mgmt-common/translib/transformer/` | Go transformer |
| `AAA_Klish_CLI_HLD.md` | `sonic-mgmt-framework/docs/` | This design document |

## 8. Testing

### 8.1 Unit Testing

- Test transformer functions with mock data
- Test actioner methods with mock REST responses
- Test template rendering with sample JSON

### 8.2 Integration Testing

- Test CLI commands end-to-end
- Verify ConfigDB entries after configuration
- Verify show command output matches ConfigDB state

### 8.3 Test Cases

1. Set authentication failthrough to enable/disable/default
2. Set authentication fallback to enable/disable/default
3. Set authentication debug to enable/disable/default
4. Set authentication trace to enable/disable/default
5. Set authentication login with single method
6. Set authentication login with multiple methods
7. Set authorization login methods
8. Set accounting login methods
9. Reset all settings to default using "no" commands
10. Show AAA configuration

## 9. Future Enhancements

1. Support for LDAP authentication method
2. Support for server group configuration
3. Support for per-service AAA configuration
4. Support for AAA accounting events
5. Integration with TACACS+ and RADIUS server configuration
