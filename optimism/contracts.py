from web3 import Web3

from .addresses import *
from .utils import get_provider, load_abi, determine_direction

class Contract():

    def __int__():
        pass

    def sign_and_broadcast(self, transaction):
        signed_txn = self.provider.eth.account.sign_transaction(transaction, self.account.key)
        txn_hash = self.provider.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = self.provider.eth.wait_for_transaction_receipt(txn_hash)

        return txn_hash, txn_receipt
    
class OptimismPortal(Contract):

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

        return self.sign_and_broadcast(deposit_transaction_tx)
    
    def prove_withdrawl_transaction():
        pass

    def finalize_withdrawl_transaction():
        pass

    def is_output_finalized():
        pass

class StandardBridge(Contract):
    
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
        
        deposit_eth_to_tx = self.contract.functions.depositETHTo(to, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": gas_limit,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": value
        })

        return self.sign_and_broadcast(deposit_eth_to_tx)

    def bridge_erc20():
        pass

    def bridge_erc20_to():
        pass

class CrossChainMessenger(Contract):

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

        return self.sign_and_broadcast(send_message_tx)
    
    def message_nonce(self):

        return self.contract.functions.messageNonce().call()
    
class L2OutputOracle():

    def __init__(self, account, provider=None):
            
        if provider is None:
            self.provider = get_provider()
        else:
            self.provider = provider

        self.account = account

        self.contract = self.provider.eth.contract(address=L2_OUTPUT_ORACLE, abi=load_abi("L2_OUTPUT_ORACLE"))

    def next_output_index(self):

        return self.contract.functions.nextOutputIndex().call()
    
    def get_l2_output_index_after(self, l2_block_nummer):

        return self.contract.functions.getL2OutputIndexAfter(l2_block_nummer).call()
    
    def get_l2_output_after(self, l2_block_number):

        output_root, timestamp, l2_block_number =  self.contract.functions.getL2OutputAfter(l2_block_number).call()

        return output_root.hex(), timestamp, l2_block_number
    
    def get_l2_output(self, l2_output_index):

        output_root, timestamp, l2_block_number =  self.contract.functions.getL2Output(l2_output_index).call()

        return output_root.hex(), timestamp, l2_block_number