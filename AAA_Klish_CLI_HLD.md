# AAA Klish CLI High-Level Design

## 1. Architecture Overview

This implementation migrates SONiC AAA (Authentication, Authorization, and Accounting) CLI commands from Click-based (sonic-utilities) to Klish-based (sonic-mgmt-framework) using the three-layer architecture:

1. **XML Definitions** (`aaa.xml`): Klish CLI command structure with parameter types and action bindings
2. **Python Actioner** (`sonic_cli_aaa.py`): REST API client that translates CLI inputs to OpenConfig REST calls
3. **Jinja2 Template** (`show_aaa.j2`): Renders REST API responses into human-readable CLI output

The transformation layer in sonic-mgmt-common handles bidirectional conversion:

4. **YANG Annotations** (`openconfig-aaa-annot.yang`): Maps OpenConfig AAA paths to SONiC DB tables/fields
5. **Go Transformer** (`xfmr_aaa.go`): Implements field and key transformers for data conversion

### Data Flow

```
CLI Input -> XML Parser -> Python Actioner -> REST API -> Transformer -> ConfigDB
ConfigDB -> Transformer -> REST API -> Python Actioner -> Jinja2 Template -> CLI Output
```

## 2. Command Mapping Table

| Click Command | Klish Command | OpenConfig Path | SONiC DB |
|---|---|---|---|
| `config aaa authentication failthrough enable` | `aaa authentication failthrough enable` | `/openconfig-aaa:aaa/authentication/config/failthrough` | `AAA\|authentication\|failthrough` |
| `config aaa authentication fallback enable` | `aaa authentication fallback enable` | `/openconfig-aaa:aaa/authentication/config/fallback` | `AAA\|authentication\|fallback` |
| `config aaa authentication debug enable` | `aaa authentication debug enable` | `/openconfig-aaa:aaa/authentication/config/debug` | `AAA\|authentication\|debug` |
| `config aaa authentication login tacacs+ local` | `aaa authentication login tacacs+ local` | `/openconfig-aaa:aaa/authentication/config/authentication-method` | `AAA\|authentication\|login` |
| `config aaa authorization local` | `aaa authorization login local` | `/openconfig-aaa:aaa/authorization/config/authorization-method` | `AAA\|authorization\|login` |
| `config aaa accounting disable` | `aaa accounting login disable` | `/openconfig-aaa:aaa/accounting/config/accounting-method` | `AAA\|accounting\|login` |
| `show aaa` | `show aaa` | `/openconfig-aaa:aaa` | AAA table |

## 3. Transformer Design

### 3.1 Key Transformer (`aaa_tbl_key_xfmr`)

OpenConfig uses separate containers (`authentication`, `authorization`, `accounting`) while SONiC uses a single `AAA` table with `type` as the key. The key transformer maps the URI path to the appropriate key:

- `/aaa/authentication/...` -> key `"authentication"`
- `/aaa/authorization/...` -> key `"authorization"`
- `/aaa/accounting/...` -> key `"accounting"`

### 3.2 Field Transformers

**Authentication Method** (`aaa_auth_method_xfmr`):
- OpenConfig: `leaf-list authentication-method` (ordered list of strings/identityrefs)
- SONiC: `leaf login` (comma-separated string, e.g., `"tacacs+,local"`)
- YangToDb: `["tacacs+", "local"]` -> `"tacacs+,local"`
- DbToYang: `"tacacs+,local"` -> `["tacacs+", "local"]`

**Authorization Method** (`aaa_authz_method_xfmr`): Same pattern as authentication.

**Accounting Method** (`aaa_acct_method_xfmr`): Same pattern as authentication.

**Boolean Fields** (failthrough, fallback, debug): Direct mapping via `sonic-ext:field-name` annotations. No custom transformer needed as the framework handles boolean conversion automatically.

## 4. Example Workflows

### 4.1 Configuration Command Flow

```
User: aaa authentication login tacacs+ local

1. XML Parser: Extracts method parameters
2. Actioner: Calls PATCH /restconf/data/openconfig-aaa:aaa/authentication/config/authentication-method
   Body: {"openconfig-aaa:authentication-method": ["tacacs+", "local"]}
3. Transformer (YangToDb_aaa_auth_method_xfmr):
   Converts ["tacacs+", "local"] -> "tacacs+,local"
4. ConfigDB: SET AAA|authentication login "tacacs+,local"
```

### 4.2 Show Command Flow

```
User: show aaa

1. XML Parser: Triggers show action
2. Actioner: Calls GET /restconf/data/openconfig-aaa:aaa
3. Transformer (DbToYang): Reads AAA table entries
   - AAA|authentication: login="tacacs+,local", failthrough="True"
   - Converts to OpenConfig JSON structure
4. Actioner: Passes response to show_aaa.j2 template
5. Template: Renders output:
   AAA authentication login tacacs+, local
   AAA authentication failthrough True
```

## 5. Files Created

| File | Repository | Purpose |
|---|---|---|
| `CLI/clitree/cli-xml/aaa.xml` | sonic-mgmt-framework | Klish XML command definitions |
| `CLI/actioner/sonic_cli_aaa.py` | sonic-mgmt-framework | Python REST API actioner |
| `CLI/renderer/templates/show_aaa.j2` | sonic-mgmt-framework | Jinja2 show output template |
| `models/yang/annotations/openconfig-aaa-annot.yang` | sonic-mgmt-common | YANG annotation mappings |
| `translib/transformer/xfmr_aaa.go` | sonic-mgmt-common | Go transformer functions |

## 6. YANG Model References

- **OpenConfig**: `openconfig-aaa.yang` (sonic-mgmt-common/models/yang/common/)
- **SONiC Native**: `sonic-system-aaa.yang` (sonic-buildimage/src/sonic-yang-models/yang-models/)
