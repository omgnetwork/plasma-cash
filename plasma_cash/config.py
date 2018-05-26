import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

plasma_config = dict(
    ROOT_CHAIN_CONTRACT_ADDRESS='0xda52B0A0a040BFeAb711065cB69321ebAE9bB96f',
    AUTHORITY=b';\x08\x84\xf4\xe5\x0e\x9b\xc2\xce\x9b"J\xb7/\xea\x89\xa8\x1c\xdf|',
    AUTHORITY_KEY=b'\xa1\x89i\x81|,\xef\xad\xf5+\x93\xeb \xf9\x17\xdc\xe7`\xce\x13\xb2\xac\x90%\xe06\x1a\xd1\xe7\xa1\xd4H',
)

"""
db_config = {
    'type': 'leveldb' | 'memory' (required)
    'path': '' (optional, if nor specific set, would have default path)
}
"""
db_config = {
    'type': 'memory'
}
