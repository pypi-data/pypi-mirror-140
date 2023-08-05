<h1 align="center">Pyzantium</h1>

<p align="center">
  <a href="https://www.codefactor.io/repository/github/rezamahdi/pyzantium">
    <img src="https://img.shields.io/codefactor/grade/github/rezamahdi/pyzantium?color=ff69b4&style=for-the-badge">
  </a>
  <a href="https://pypi.org/">
    <img src="https://img.shields.io/pypi/v/pyzantium?style=for-the-badge">
  </a>
  <a href="https://pypi.org/project/pyzantium/">
    <img src="https://img.shields.io/pypi/pyversions/pyzantium?style=for-the-badge">
  </a>
  <a href="/LICENSE">
    <img src="https://img.shields.io/github/license/rezamahdi/pyzantium?color=darkred&style=for-the-badge">
  </a>
  <a href="https://github.com/rezamahdi/pyzantium/commits">
    <img src="https://img.shields.io/github/last-commit/rezamahdi/pyzantium?style=for-the-badge">
  </a>
  <a href="https://github.com/rezamahdi/pyzantium/releases">
    <img src="https://img.shields.io/github/release-date/rezamahdi/pyzantium?color=teal&style=for-the-badge">
  </a>
  <a href="https://github.com/rezamahdi/pyzantium/issues">
    <img src="https://img.shields.io/github/issues-raw/rezamahdi/pyzantium?color=blueviolet&style=for-the-badge">
  </a>
</p>

<p align="center">
  <a href="https://github.com/rezamahdi/pyzantium/issues/new?assignees=rezamahdi&labels=bug&late=BUG_REPORT.md&title=%5BBUG%5D%3A">Report Bug
  </a>
  ·
  <a href="https://github.com/rezamahdi/pyzantium/issues/new?assignees=rezamahdi&labels=enhancement&late=FEATURE_REQUEST.md&title=%5BFEATURE%5D%3A">Request Feature
  </a>
</p>

---

> 🔗 Python implementation and building blocks for blockchain

Pyzantium is a python module that let you implement blockchain whit various capabilityies
in your project.

The Module provide both high-level(`Blockchain`) and low-level(`Block`,`Consensus`, ...)
classes in order to be highly customizable.

---

- [1. Installation](#1-installation)
- [2. Usage](#2-usage)
- [3. License](#3-license)

## 1. Installation

The package is pip installable:
```bash
pip install pybchain
```

Or, you can download it and use `setuptools` to build it by hand:
```bash
git clone http://github.com/rezamahdi/pybchain
cd pybchain
python setup.py install
```


## 2. Usage

To initialize a blockchain, you must specify some info as agreement:

- Hash algorithm to use in blockchain.
- Wath type of data you want to store. Blockchain is capable of storing anythin
   not only transactions.
- An authentication scheme. Common way to do this is using ECC. this part is optional.
- Endpoint to connect to other nodes. Common option is a HTTP api or json-rpc.

Whit having these options specified, you can initialize the node as this:

```python
from pyzantium import Chain, Block
from pyzantium.storage import Disk
from hashlib import sha_256

chain = Chain(
  hash=sha_256,
  storage=Disk(
    "path/to/storage",
    create=True
  )
)
```

Next, in order to mine genesis block do this:
```python
genesis = Block(chain)
genesis.add_part(b'000000000000000000000000000')  # or any other type of data.
# add more data parts...
genesis.finalize()  # we don't use `mine` because it is named `forge` in PoS.

result = endpoint.broadcast_new_block(genesis)

if result.is_ok():
  chain.append(genesis)
```

see [documentation](http://pyzantium.readthedocs.org) for more info

## 3. License
Copyright (c) Reza Mahdi 2022
This project is licensed under terms of MIT License (see LICENSE)