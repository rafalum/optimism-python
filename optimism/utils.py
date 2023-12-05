import os
import json

from web3 import Web3
from dotenv import load_dotenv

from .constants import MESSAGE_PASSED_ID
from .types import MessagePassedEvent, StateTrieProof

load_dotenv()

def get_env_variable(var_name):
    return os.environ.get(var_name)

def get_provider(chain_id):

    if is_chain_supported(chain_id) is False:
        raise Exception(f"Chain ID {chain_id} not supported: add it to the config.json file or open a request to add it.")
    
    provider_url = get_env_variable("PROVIDER_URL_" + str(chain_id))

    return Web3(Web3.HTTPProvider(provider_url))

def get_account(chain_id):

    if is_chain_supported(chain_id) is False:
        raise Exception(f"Chain ID {chain_id} not supported: add it to the config.json file or open a request to add it.")
    
    pk = get_env_variable("PRIVATE_KEY_" + str(chain_id))

    return get_provider(chain_id).eth.account.from_key(pk)

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

def log_to_address(log):

    return Web3.to_checksum_address("0x" + log[-40:])

def to_low_level_message(txn, txn_receipt):

    logs = txn_receipt.logs

    for log in logs:
        if log.topics[0].hex() == MESSAGE_PASSED_ID:
            message_passed_log = log
            break

    message_length = int(message_passed_log.data[128:160].hex(), 16)

    return MessagePassedEvent(
        message_nonce=int(message_passed_log.topics[1].hex(), 16),
        sender=log_to_address(message_passed_log.topics[2].hex()),
        target=log_to_address(message_passed_log.topics[3].hex()),
        value=int(message_passed_log.data[:32].hex(), 16),
        min_gas_limit=int(message_passed_log.data[32:64].hex(), 16),
        message=message_passed_log.data[160:160 + message_length].hex()
    ), message_passed_log.data[96:128].hex()

def make_state_trie_proof(provider, block_number, address, slot):

    proof = provider.eth.get_proof(address, [slot], block_identifier=block_number)

    return StateTrieProof(
        account_proof=proof.accountProof,
        storage_proof=proof.storageProof[0].proof,
        storage_value=proof.storageProof[0].value,
        storage_root=proof.storageHash
    )

def is_chain_supported(chain_id):

    l1_chain_ids = get_l1_chain_ids()
    l2_chain_ids = get_l2_chain_ids()
    
    return str(chain_id) in l1_chain_ids or str(chain_id) in l2_chain_ids

def read_addresses(chain_id_l1, chain_id_l2, layer="l1"):

    path = f"{os.path.dirname(os.path.abspath(__file__))}"
    with open(os.path.abspath(path + f"/config.json")) as f:
        addresses: dict = json.load(f)

    return addresses[str(chain_id_l1)][str(chain_id_l2)][layer + "_addresses"]

    
def get_l1_chain_ids():
    path = f"{os.path.dirname(os.path.abspath(__file__))}"
    with open(os.path.abspath(path + f"/config.json")) as f:
        addresses: dict = json.load(f)

    return addresses.keys()

def get_l2_chain_ids():
    path = f"{os.path.dirname(os.path.abspath(__file__))}"
    with open(os.path.abspath(path + f"/config.json")) as f:
        addresses: dict = json.load(f)

    l1_chain_ids = addresses.keys()
    l2_chain_ids = []
    for id in l1_chain_ids:
        l2_chain_ids += addresses[id].keys()

    return l2_chain_ids

