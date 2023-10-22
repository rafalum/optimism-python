from web3 import Web3

from .addresses import *
from .utils import get_provider, load_abi, determine_direction

class OptimismPortal():

    def __init__(self, account, provider=None):
        
        if provider is None:
            self.provider = get_provider()
        else:
            self.provider = provider
        
        self.account = account
        self.contract = self.provider.eth.contract(address=OPTIMISM_PORTAL, abi=load_abi("OPTIMISM_PORTAL"))

    def deposit_transaction(self, to, value, gas_limit, is_creation, data):
        
        deposit_transaction_tx = self.contract.functions.depositTransaction(to, value, gas_limit, is_creation, data).build_transaction({
            "from": self.account.address,
            "gas": gas_limit,
            "value": value,
            "nonce": self.provider.eth.get_transaction_count(self.account.address)
        })

        signed_txn = self.provider.eth.account.sign_transaction(deposit_transaction_tx, self.account.key)
        txn_hash = self.provider.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = self.provider.eth.wait_for_transaction_receipt(txn_hash)

        return txn_hash, txn_receipt
    
    def prove_withdrawl_transaction():
        pass

    def finalize_withdrawl_transaction():
        pass

    def is_output_finalized():
        pass

class StandardBridge():
    
    def __init__(self, account, from_chain_id=1, to_chain_id=10, provider=None):
        
        l1_to_l2 = determine_direction(from_chain_id, to_chain_id)
        l2 = not l1_to_l2

        if provider is None:
            self.provider = get_provider(l2=l2)
        else:
            self.provider = provider
        
        self.from_chain_id = from_chain_id
        self.to_chain_id = to_chain_id

        self.account = account

        if l1_to_l2:
            self.contract = self.provider.eth.contract(address=L1_STANDARD_BRIDGE, abi=load_abi("L1_STANDARD_BRIDGE"))
        else:
            self.contract = self.provider.eth.contract(address=L2_STANDARD_BRIDGE, abi=load_abi("L2_STANDARD_BRIDGE"))

    def bridge_eth():
        pass
    
    def deposit_eth_to(self, to, gas_limit, extra_data, value):
        
        deposti_eth_to_tx = self.contract.functions.depositETHTo(to, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": gas_limit,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": value
        })

        signed_txn = self.provider.eth.account.sign_transaction(deposti_eth_to_tx, self.account.key)
        txn_hash = self.provider.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = self.provider.eth.wait_for_transaction_receipt(txn_hash)

        return txn_hash, txn_receipt

    def bridge_erc20():
        pass

    def bridge_erc20_to():
        pass

class CrossChainMessenger():

    def __init__(self, account, from_chain_id=1, to_chain_id=10, to_l2=True, provider=None):

        l1_to_l2 = determine_direction(from_chain_id, to_chain_id)
        l2 = not l1_to_l2

        if provider is None:
            self.provider = get_provider(l2=l2)
        else:
            self.provider = provider
        
        self.from_chain_id = from_chain_id
        self.to_chain_id = to_chain_id

        self.account = account

        if l1_to_l2:
            self.contract = self.provider.eth.contract(address=L1_CROSS_CHAIN_MESSENGER, abi=load_abi("L1_CROSS_MESSENGER"))
        else:
            self.contract = self.provider.eth.contract(address=L2_CROSS_CHAIN_MESSENGER, abi=load_abi("L2_CROSS_MESSENGER"))


    def send_message(self, target, message, min_gas_limit, value=None):

        send_message_tx = self.contract.functions.sendMessage(target, message, min_gas_limit).build_transaction({
            "from": self.account.address,
            "gas": min_gas_limit,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": 0 if value is None else value
        })

        signed_txn = self.provider.eth.account.sign_transaction(send_message_tx, self.account.key)
        txn_hash = self.provider.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = self.provider.eth.wait_for_transaction_receipt(txn_hash)

        return txn_hash, txn_receipt
    
    def message_nonce(self):

        return self.contract.functions.messageNonce().call()