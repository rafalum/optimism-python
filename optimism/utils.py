import os
import json

from web3 import Web3
from dotenv import load_dotenv

from .constants import MESSAGE_PASSED_ID
from .types import MessagePassedEvent, StateTrieProof

load_dotenv()

def get_env_variable(var_name):
    return os.environ.get(var_name)

def get_provider(l2=False, network="mainnet"):

    if is_network_supported(network) is False:
        raise Exception(f"Network {network} not supported: add it to the addresses.py file")
    
    provider_url = get_env_variable(str.upper(network) + "_PROVIDER_URL_" + ("L2" if l2 else "L1"))

    return Web3(Web3.HTTPProvider(provider_url))

def get_account(l2=False, network="mainnet"):

    if is_network_supported(network) is False:
        raise Exception(f"Network {network} not supported: add it to the addresses.py file")
    
    pk = get_env_variable("PRIVATE_KEY_" + ("L2" if l2 else "L1"))

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

def is_network_supported(network):

    l1_addresses = read_addresses("l1")
    networks = l1_addresses.keys()

    for net in networks:
        if network in net:
            return True
    
    return False

def read_addresses(layer):

    path = f"{os.path.dirname(os.path.abspath(__file__))}"
    with open(os.path.abspath(path + f"/addresses.json")) as f:
        addresses: dict = json.load(f)

    if layer == "l1":
        return addresses["l1_addresses"]
    elif layer == "l2":
        return addresses["l2_addresses"]
    else:
        raise Exception("Layer must be l1 or l2")