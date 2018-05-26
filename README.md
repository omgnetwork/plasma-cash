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
FLASK_APP=plasma_cash/child_chain FLASK_ENV=develment flask run --port=8546
```

Client:
```
python
>>> from plasma_cash.dependency_config import container
>>> c = container.get_client()
>>> c.deposit(100, '0xb83e232458a092696be9717045d9a605fb0fec2b', '0x0000000000000000000000000000000000000000')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.send_transaction(1, 1693390459388381052156419331572168595237271043726428428352746834777341368960, 100, '0x08d92dca9038ea9433254996a2d4f08d43be8227', '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b')
>>> c.submit_block('0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448')
>>> c.start_exit('0x08d92dca9038ea9433254996a2d4f08d43be8227', 1693390459388381052156419331572168595237271043726428428352746834777341368960, 1, 2)
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
