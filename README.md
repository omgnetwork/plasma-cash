# plasma-cash

[![codecov](https://codecov.io/gh/omisego/plasma-cash/branch/master/graph/badge.svg)](https://codecov.io/gh/omisego/plasma-cash)

### Dependency Prerequisite

- [LevelDB](https://github.com/google/leveldb)

Mac:
```
$ brew install leveldb
```

Linux:

LevelDB should be installed along with `plyvel` once you make the project later on.

Windows:

First, install [vcpkg](https://github.com/Microsoft/vcpkg). Then,

```
> vcpkg install leveldb
```

- [Solidity 0.4.24](https://github.com/ethereum/solidity/releases/tag/v0.4.24)

Mac:
```
$ brew update
$ brew upgrade
$ brew tap ethereum/ethereum
$ brew install solidity
```

Linux:
```
$ wget https://github.com/ethereum/solidity/releases/download/v0.4.24/solc-static-linux
$ chmod +x ./solc-static-linux
$ sudo mv solc-static-linux /usr/bin/solc
```

Windows:

Follow [this guide](https://solidity.readthedocs.io/en/v0.4.21/installing-solidity.html#prerequisites-windows).

- [ganache-cli 6.1.2+](https://github.com/trufflesuite/ganache-cli)

It's also recommended to run `ganache-cli` when developing, testing, or playing around. This will allow you to receive near instant feedback.

Mac:
```
$ brew install node
$ npm install -g ganache-cli
```

Linux:

Install [Node.js](https://nodejs.org/en/download/). Then,
```
$ npm install -g ganache-cli
```

- [Python 3.5+](https://www.python.org/downloads/)

### Develop

Install requirements:
```
pip install -r requirements.txt
```

Ganache-cli command:
```
ganache-cli -m=plasma_cash
```

Deploy contract:
```
python deployment.py
```

Run child chain Server:
```
python -m plasma_cash.child_chain
```

Run operator cron jobs:
(TODO: the following commands does not support running with cron job yet)
```
python -m plasma_cash.operator_cron_job
```

Client:
```
python
>>> from web3.auto import w3
>>> from plasma_cash.client.client import Client
>>> from plasma_cash.dependency_config import container
>>> operator_key = '0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448'
>>> userA_key = '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b'
>>> userB_key = '0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30'
>>> operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
>>> userA = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
>>> userB = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
>>> userA.deposit(10, '0x0000000000000000000000000000000000000000')
>>> operator.submit_block()
>>> userA.send_transaction(1, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0x08d92dca9038ea9433254996a2d4f08d43be8227')
>>> operator.submit_block()
>>> userB.start_exit(1693390459388381052156419331572168595237271043726428428352746834777341368960, 1, 2)
>>> w3.providers[0].make_request('evm_increaseTime', 60 * 60 * 24 * 14)  # force ganache to increase time for two week
>>> userB.finalize_exit(1693390459388381052156419331572168595237271043726428428352746834777341368960)
```

(Challenge spent coin)
```
python
>>> from plasma_cash.client.client import Client
>>> from plasma_cash.dependency_config import container
>>> operator_key = '0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448'
>>> userA_key = '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b'
>>> userB_key = '0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30'
>>> userC_key = '0x8af3051eb765261b245d586a88700e606431b199f2cce4c825d2b1921086b35c'
>>> operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
>>> userA = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
>>> userB = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
>>> userC = Client(container.get_root_chain(), container.get_child_chain_client(), userC_key)
>>> userA.deposit(10, '0x0000000000000000000000000000000000000000')
>>> operator.submit_block()
>>> userA.send_transaction(1, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0x08d92dca9038ea9433254996a2d4f08d43be8227')
>>> operator.submit_block()
>>> userB.send_transaction(2, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0xdf29cfbd5d793fa5b22d5c730a8e8450740c6f8f')
>>> operator.submit_block()
>>> userB.start_exit(1693390459388381052156419331572168595237271043726428428352746834777341368960, 1, 2)
>>> operator.submit_block()
>>> userC.challenge_exit(1693390459388381052156419331572168595237271043726428428352746834777341368960, 3)
```
(Challenge history and respond)
```
python
>>> from plasma_cash.client.client import Client
>>> from plasma_cash.dependency_config import container
>>> operator_key = '0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448'
>>> userA_key = '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b'
>>> userB_key = '0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30'
>>> userC_key = '0x8af3051eb765261b245d586a88700e606431b199f2cce4c825d2b1921086b35c'
>>> userD_key = '0x4d4c362239f610305b1c05ef91928c893d9a631e08149b7d66286fcf3dfa8553'
>>> operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
>>> userA = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
>>> userB = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
>>> userC = Client(container.get_root_chain(), container.get_child_chain_client(), userC_key)
>>> userD = Client(container.get_root_chain(), container.get_child_chain_client(), userD_key)
>>> userA.deposit(10, '0x0000000000000000000000000000000000000000')
>>> operator.submit_block()
>>> userA.send_transaction(1, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0x08d92dca9038ea9433254996a2d4f08d43be8227')
>>> operator.submit_block()
>>> userB.send_transaction(2, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0xdf29cfbd5d793fa5b22d5c730a8e8450740c6f8f')
>>> operator.submit_block()
>>> userC.send_transaction(3, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0xc5016a1dc1f2556fd237abba2681d221edf31a20')
>>> operator.submit_block()
>>> userD.start_exit(1693390459388381052156419331572168595237271043726428428352746834777341368960, 3, 4)
>>> userC.challenge_exit(1693390459388381052156419331572168595237271043726428428352746834777341368960, 1)
>>> userD.respond_challenge_exit(b'\xf8{\x80\xa0\x03\xbel\xcf\x13%K@a\xd1\x86\xa8v\\\xd2\xe0Iw\x8c|g\xd0\xe3\x02&\x8d\x15^"W\x1a\x80\n\x94\xb8>#$X\xa0\x92ik\xe9qpE\xd9\xa6\x05\xfb\x0f\xec+\xb8A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 1693390459388381052156419331572168595237271043726428428352746834777341368960, 2)
```

Run unit tests:
```
pytest unit_tests
```

Run integration tests:
```
behave integration_tests/features/
```

Run linter:
```
flake8 plasma_cash/
flake8 unit_tests/
flake8 integration_tests/
```
