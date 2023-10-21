from web3 import Web3

from .addresses import *
from .utils import get_provider, load_abi

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
    
    def __init__():
        pass

    def bridge_eth():
        pass
    
    def bridge_eth_to():
        pass

    def bridge_erc20():
        pass

    def bridge_erc20_to():
        pass

class CrossChainMessenger():

    def __init__():
        pass


    def send_message():
        pass
    
    def message_nonce():
        pass