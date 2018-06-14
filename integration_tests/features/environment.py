import os
import signal
import time
from subprocess import Popen

from plasma_cash.root_chain.deployer import Deployer

root_chain_process = None
child_chain_process = None


def before_scenario(context, step):
    global root_chain_process
    global child_chain_process
    root_chain_process = spin_up_root_chain()
    time.sleep(5)
    deploy_contracts()
    time.sleep(1)
    child_chain_process = spin_up_child_chain_server()
    time.sleep(1)


def after_scenario(context, step):
    os.killpg(os.getpgid(child_chain_process.pid), signal.SIGTERM)
    os.killpg(os.getpgid(root_chain_process.pid), signal.SIGTERM)


def spin_up_root_chain():
    return Popen(['ganache-cli', '-m=plasma_cash'], preexec_fn=os.setsid)


def deploy_contracts():
    Deployer().deploy_contract('RootChain/RootChain.sol')


def spin_up_child_chain_server():
    my_env = os.environ.copy()
    my_env.update({
        'FLASK_APP': 'plasma_cash/child_chain'
    })
    return Popen(['flask', 'run', '--port=8546'], env=my_env, preexec_fn=os.setsid)
