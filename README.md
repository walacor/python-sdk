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

## Overview

This repository provides a Python SDK for interacting with the [Walacor](https://example.com) platform. The Walacor platform leverages immutable versioning (backed by blockchain), schema management, and data provenance features to offer a tamper-proof data lifecycle. The SDK abstracts away low-level API calls and cryptographic details, letting users focus on **secure data ingestion**, **provenance tracking**, and **data transformations** in a Pythonic manner.


---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **pip** for package management.
- A valid **Walacor** account or dev sandbox environment.

### Installation

#### From Source (Development Mode)
```bash
git clone https://github.com/walacor/python-sdk
cd walacor-sdk
pip install -e .
```

#### From PyPI
```bash
pip install walacor-python-sdk
```

### Configuration

Set up authentication (Preview)
```python
from walacor_sdk.api.authentication import WalacorAuth

auth = WalacorAuth(url="https://example-walacor.com", username="W_username", password="W_password")
```

---

## Testing & CI/CD

- **Pytest** for unit tests.

```bash
pip install .[test]
pytest
```
---

## 🚀 Contributing

We welcome contributions! Please follow our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

- **Do NOT push directly to `main`**.
- Follow the [branching strategy](CONTRIBUTING.md#-branching-strategy).
- Ensure your changes pass **CI/CD checks** before merging.

For full contribution details, see 👉 [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

This project is licensed under the **Apache 2.0 License** - see the [LICENSE](LICENSE) file for details.

---

