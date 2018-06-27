# plasma-cash

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

- [Solidity 0.4.18](https://github.com/ethereum/solidity/releases/tag/v0.4.18)

Mac:
```
$ brew unlink solidity
$ brew install https://raw.githubusercontent.com/ethereum/homebrew-ethereum/2aea171d7d6901b97d5f1f71bd07dd88ed5dfb42/solidity.rb
```

Linux:
```
$ wget https://github.com/ethereum/solidity/releases/download/v0.4.18/solc-static-linux
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

- [Python 3.2+](https://www.python.org/downloads/)

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

Run child chain:
```
FLASK_APP=plasma_cash/child_chain flask run --port=8546
```

Client:
```
python
>>> from plasma_cash.dependency_config import container
>>> c = container.get_client()
>>> c.deposit(10, '0xb83e232458a092696be9717045d9a605fb0fec2b', '0x0000000000000000000000000000000000000000')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.send_transaction(1, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0x08d92dca9038ea9433254996a2d4f08d43be8227', '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.start_exit('0x08d92dca9038ea9433254996a2d4f08d43be8227', 1693390459388381052156419331572168595237271043726428428352746834777341368960, 1, 2)
```

(Challenge double spending)
```
python
>>> from plasma_cash.dependency_config import container
>>> c = container.get_client()
>>> c.deposit(10, '0xb83e232458a092696be9717045d9a605fb0fec2b', '0x0000000000000000000000000000000000000000')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.send_transaction(1, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0x08d92dca9038ea9433254996a2d4f08d43be8227', '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.send_transaction(2, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0xdf29cfbd5d793fa5b22d5c730a8e8450740c6f8f', '0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30')
>>> c.start_exit('0x08d92dca9038ea9433254996a2d4f08d43be8227', 1693390459388381052156419331572168595237271043726428428352746834777341368960, 1, 2)
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.challenge_exit('0xdf29cfbd5d793fa5b22d5c730a8e8450740c6f8f', 1693390459388381052156419331572168595237271043726428428352746834777341368960, 3)
```
(Challenge history and respond)
```
>>> from plasma_cash.dependency_config import container
>>> c = container.get_client()
>>> c.deposit(10, '0xb83e232458a092696be9717045d9a605fb0fec2b', '0x0000000000000000000000000000000000000000')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.send_transaction(1, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0x08d92dca9038ea9433254996a2d4f08d43be8227', '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.send_transaction(2, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0xdf29cfbd5d793fa5b22d5c730a8e8450740c6f8f', '0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.send_transaction(3, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 10, '0xc5016a1dc1f2556fd237abba2681d221edf31a20', '0x8af3051eb765261b245d586a88700e606431b199f2cce4c825d2b1921086b35c')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.start_exit('0xc5016a1dc1f2556fd237abba2681d221edf31a20', 1693390459388381052156419331572168595237271043726428428352746834777341368960, 3, 4)
>>> c.challenge_exit('0xdf29cfbd5d793fa5b22d5c730a8e8450740c6f8f', 1693390459388381052156419331572168595237271043726428428352746834777341368960, 1)
>>> c.respond_challenge_exit('0xc5016a1dc1f2556fd237abba2681d221edf31a20', b'\xf8{\x80\xa0\x03\xbel\xcf\x13%K@a\xd1\x86\xa8v\\\xd2\xe0Iw\x8c|g\xd0\xe3\x02&\x8d\x15^"W\x1a\x80\n\x94\xb8>#$X\xa0\x92ik\xe9qpE\xd9\xa6\x05\xfb\x0f\xec+\xb8A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 1693390459388381052156419331572168595237271043726428428352746834777341368960, 2)
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
