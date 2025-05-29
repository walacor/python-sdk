# Walacor Python SDK

<div align="center">

<img src="https://www.walacor.com/wp-content/uploads/2022/09/Walacor_Logo_Tag.png" width="300" />

[![License Apache 2.0][badge-license]][license]
[![Walacor (1100127456347832400)](https://img.shields.io/badge/My-Discord-%235865F2.svg?label=Walacor)](https://discord.gg/BaEWpsg8Yc)
[![Walacor (1100127456347832400)](https://img.shields.io/static/v1?label=Walacor&message=LinkedIn&color=blue)](https://www.linkedin.com/company/walacor/)
[![Walacor (1100127456347832400)](https://img.shields.io/static/v1?label=Walacor&message=Website&color)](https://www.walacor.com/product/)

</div>

[badge-license]: https://img.shields.io/badge/license-Apache2-green.svg?dummy
[license]: https://github.com/walacor/objectvalidation/blob/main/LICENSE


# Walacor Python SDK

[![PyPI](https://img.shields.io/pypi/v/walacor-python-sdk.svg)](https://pypi.org/project/walacor-python-sdk/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

*A typed, lightweight wrapper around Walacor’s REST API for immutable provenance, schema management and (soon) data‑science transformations.*

---

## ✨ Features

* **One‑liner setup** – a single `WalacorService` object bootstraps authentication and exposes sub‑clients (`auth`, `schema`, `data`, *etc.*)
* **Pydantic models everywhere** – rich typing, runtime validation and IDE autocompletion.
* **Version‑safe schemas** – helper methods to list, inspect and create schema blueprints.
* **Composable requests** – thin wrappers over `requests` that automatically inject Bearer tokens and headers.
* **Python 3.11 + only** – enjoy `typing` generics, `|` unions, `match` statements.

---

## 📦 Installation

### From PyPI (recommended)

```bash
pip install walacor-python-sdk
```

### From source (editable)

```bash
git clone https://github.com/walacor/python-sdk.git
cd python-sdk
pip install -e .[dev,test]
```

> After installation, import via `walacor_sdk` (underscore), **not** the PyPI name with a dash.

```python
from walacor_sdk import WalacorService
```

---

## 🚀 Quick Start

### 1 – Create a service instance

```python
from walacor_sdk import WalacorService

wal = WalacorService(
    server="http://[walacor.instance.address/api",
    username="Admin",
    password="Password!"
)
```

Need to change credentials later?

```python
wal.changeCred("new_user", "new_password")
```

### 2 – Work with schemas

```python
from walacor_sdk.schema.models import (
    CreateSchemaRequest, CreateSchemaDefinition,
    CreateFieldRequest, CreateIndexRequest
)

schema_req = CreateSchemaRequest(
    ETId=50,    # system envelope for schemas
    SV=1,
    Schema=CreateSchemaDefinition(
        ETId=654321,
        TableName="books",
        Family="library",
        DoSummary=True,
        Fields=[
            CreateFieldRequest(FieldName="book_id", DataType="TEXT", Required=True),
            CreateFieldRequest(FieldName="title",   DataType="TEXT", Required=True)
        ],
        Indexes=[
            CreateIndexRequest(Fields=["book_id"], IndexValue="book_id")
        ]
    )
)

meta = wal.schema.create_schema(schema_req)
print("Created schema envelope:", meta.EId)
```

Other handy calls:

```python
# list latest versions for every ETId
for s in wal.schema.get_list_with_latest_version():
    print(s.ETId, s.TableName)

# detailed info for a known ETId
info = wal.schema.get_schema_details_with_ETId(654321)
print(info.Fields)
```

### 3 – Use enums & constants

```python
from walacor_sdk.utils.enums import SystemEnvelopeType
print(SystemEnvelopeType.SCHEMA.value)   # -> 50
```

---

## ⚙️ Error handling & logging

* Network errors raise `requests.HTTPError` so you can retry or surface gracefully.
* Validation errors are logged with `logging.error` and result in `None`/`[]` returns, never raw dictionaries.
* The SDK writes to the module‑level *walacor\_sdk.utils.logger* logger; attach your own handler or redirect to file.

---

## 🧪 Running tests

```bash
pip install .[test]
pytest -q
```

---

## 🤝 Contributing

We love PRs! Please open an issue first for large features. All contributions must:

* Pass `pre-commit` hooks (`pre-commit run --all-files`).
* Include unit tests with `pytest`.
* Follow the existing docstring & typing style.

For full contribution details, see 👉 [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

Apache 2.0 © 2025 Walacor & Contributors.
