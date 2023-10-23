import os
import math
import json
import sha3
import numpy as np

from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(var_name):
    return os.environ.get(var_name)

def get_provider(l2=False, network="mainnet"):
    if l2:
        provider_url = get_env_variable("PROVIDER_L2" + ("_" + str.upper(network) if network != "mainnet" else ""))
    else:
        provider_url = get_env_variable("PROVIDER_L1" + ("_" + str.upper(network) if network != "mainnet" else ""))

    return Web3(Web3.HTTPProvider(provider_url))

def get_account(l2=False, network="mainnet"):
    if l2:
        pk = get_env_variable("PRIVATE_KEY_L2")
    else:
        pk = get_env_variable("PRIVATE_KEY_L1")

    return get_provider(l2=l2, network=network).eth.account.from_key(pk)

def load_abi(name: str) -> str:

    abi = name.lower()

    path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/"
    with open(os.path.abspath(path + f"{abi}.json")) as f:
        abi: str = json.load(f)
    return abi

def determine_direction(from_chain_id, to_chain_id):
    if from_chain_id < to_chain_id:
        return True
    else:
        return False
    
def hash_message_hash(message_hash: str) -> str:
    # Web3 provides utility functions similar to ethers
    w3 = Web3()
    
    # These are equivalent constants in web3.py for ethers.constants.HashZero
    HASH_ZERO = int('0x0000000000000000000000000000000000000000000000000000000000000000', 16)
    
    # Use solidityKeccak for both encoding and hashing
    return w3.solidity_keccak(['bytes32', 'uint256'], [message_hash, HASH_ZERO]).hex()