# plasma-cash

Install requirements:
`pip install -r requirements.txt`

Ganache-cli command:
`ganache-cli -m =plasma_cash`

Run child chain:
`FLASK_APP=plasma_cash/child_chain/server.py flask run --port=8546`

Deposit:
```
python
>>> from plasma_cash.client.client import Client
>>> c = Client()
>>> c.deposit(100, '0xb83e232458a092696be9717045d9a605fb0fec2b')
```
