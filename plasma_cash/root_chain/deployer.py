import json
import os

from solc import compile_standard
from web3 import HTTPProvider, Web3

from plasma_cash.config import plasma_config

OWN_DIR = os.path.dirname(os.path.realpath(__file__))


class Deployer(object):

    def __init__(self, provider=HTTPProvider('http://localhost:8545')):
        self.w3 = Web3(provider)

    def get_dirs(self, path):
        abs_contract_path = os.path.realpath(os.path.join(OWN_DIR, 'contracts'))

        extra_args = []
        for r, d, f in os.walk(abs_contract_path):
            for file in f:
                extra_args.append([file, [os.path.realpath(os.path.join(r, file))]])

        contracts = {}
        for contract in extra_args:
            contracts[contract[0]] = {'urls': contract[1]}
        path = '{}/{}'.format(abs_contract_path, path)
        return path, contracts

    def compile_contract(self, path, args=()):
        file_name = path.split('/')[1]
        contract_name = file_name.split('.')[0]
        path, contracts = self.get_dirs(path)
        compiled_sol = compile_standard({
            'language': 'Solidity',
            'sources': {**{path.split('/')[-1]: {'urls': [path]}}, **contracts}
        }, allow_paths=OWN_DIR + "/contracts")
        abi = compiled_sol['contracts'][file_name][contract_name]['abi']
        bytecode = compiled_sol['contracts'][file_name][contract_name]['evm']['bytecode']['object']

        # Create the contract_data folder if it doesn't already exist
        os.makedirs('contract_data', exist_ok=True)

        contract_file = open('contract_data/%s.json' % (file_name.split('.')[0]), "w+")
        json.dump(abi, contract_file)
        contract_file.close()
        return abi, bytecode, contract_name

    def deploy_contract(self, path, args=(), gas=4410000):
        abi, bytecode, contract_name = self.compile_contract(path, args)
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        # Get transaction hash from deployed contract
        tx_hash = contract.deploy(
            transaction={'from': self.w3.eth.accounts[0], 'gas': gas},
            args=args
        )

        print('Successfully deployed {} contract with tx hash {}!'.format(contract_name, tx_hash))

    def get_contract(self, path):
        file_name = path.split('/')[1]
        abi = json.load(open('contract_data/%s.json' % (file_name.split('.')[0])))
        contract = self.w3.eth.contract(
            address=plasma_config['ROOT_CHAIN_CONTRACT_ADDRESS'],
            abi=abi
        )
        return contract
