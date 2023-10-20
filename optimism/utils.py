import os
import math
import json
import numpy as np

from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(var_name):
    return os.environ.get(var_name)

def get_provider(l2=False):
    if l2:
        provider_url = get_env_variable("PROVIDER_L2")
    else:
        provider_url = get_env_variable("PROVIDER_L1")

    return Web3(Web3.HTTPProvider(provider_url))

def get_account(l2=False):
    if l2:
        pk = get_env_variable("PRIVATE_KEY_L2")
    else:
        pk = get_env_variable("PRIVATE_KEY_L1")

    return get_provider(l2=l2).eth.account.from_key(pk)

def load_abi(name: str) -> str:

    abi = name.lower()

    path = f"{os.path.dirname(os.path.abspath(__file__))}/../assets/"
    with open(os.path.abspath(path + f"{abi}.json")) as f:
        abi: str = json.load(f)
    return abi