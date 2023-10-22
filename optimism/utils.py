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
    
HASH_ZERO = "0x" + "0" * 64  # This represents the ethers.constants.HashZero in a hexadecimal format.

def hash_message_hash(message_hash: str) -> str:
    """
    Utility for hashing a message hash. This computes the storage slot
    where the message hash will be stored in state. HashZero is used
    because the first mapping in the contract is used.

    Args:
        message_hash (str): Message hash to hash.

    Returns:
        str: Hash of the given message hash.
    """

    # Encoding the message hash and HASH_ZERO. 
    # This is a basic representation; you may need to adjust depending on how your data is structured.
    data = message_hash + HASH_ZERO

    # Compute the keccak256 hash of the data
    k = sha3.keccak_256()
    k.update(data.encode())  # Assuming the input is a utf-8 encoded string.
    return "0x" + k.hexdigest()