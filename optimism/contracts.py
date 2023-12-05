from web3 import Web3

from .types import MessageStatus
from .utils import get_provider, load_abi, determine_direction, is_chain_supported, read_addresses

class Contract():

    def __int__():
        pass

    def sign_and_broadcast(self, transaction):
        signed_txn = self.provider.eth.account.sign_transaction(transaction, self.account.key)
        txn_hash = self.provider.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = self.provider.eth.wait_for_transaction_receipt(txn_hash)

        return txn_hash.hex(), txn_receipt
    
class OptimismPortal(Contract):

    def __init__(self, chain_id_l1, chain_id_l2, account, provider=None):
        
        if provider is None:
            self.provider = get_provider(chain_id_l1)
        else:
            self.provider = provider

        if is_chain_supported(chain_id_l1) is False:
            raise Exception(f"Chain ID {chain_id_l1} not supported: add it to the config.json file or open a request to add it.")
        if is_chain_supported(chain_id_l2) is False:
            raise Exception(f"Chain ID {chain_id_l2} not supported: add it to the config.json file or open a request to add it.")

        self.address = read_addresses(chain_id_l1, chain_id_l2, layer="l1")["OPTIMISM_PORTAL"]
        
        self.account = account
        self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("OPTIMISM_PORTAL"))

    def deposit_transaction(self, to, value, gas_limit, is_creation, data):
        
        deposit_transaction_tx = self.contract.functions.depositTransaction(to, value, gas_limit, is_creation, data).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "value": value,
            "nonce": self.provider.eth.get_transaction_count(self.account.address)
        })

        return self.sign_and_broadcast(deposit_transaction_tx)
    
    def prove_withdrawl_transaction(self, tx, l2_output_index, output_root_proof, withdrawl_proof):
        
        prove_withdrawl_transaction_tx = self.contract.functions.proveWithdrawalTransaction(tx, l2_output_index, output_root_proof, withdrawl_proof).build_transaction({
            "from": self.account.address,
            "gas": 1000000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address)
        })

        return self.sign_and_broadcast(prove_withdrawl_transaction_tx)

    def finalize_withdrawl_transaction(self, tx):
        
        finalize_withdrawl_transaction_tx = self.contract.functions.finalizeWithdrawalTransaction(tx).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address)
        })

        return self.sign_and_broadcast(finalize_withdrawl_transaction_tx)

    def is_output_finalized():
        pass

    def proven_withdrawls(self, withdrawl_hash):

        return self.contract.functions.provenWithdrawals(withdrawl_hash).call()

class StandardBridge(Contract):
    
    def __init__(self, account, from_chain_id, to_chain_id, provider=None):
        
        self.l1_to_l2 = determine_direction(from_chain_id, to_chain_id)

        if provider is None:
            self.provider = get_provider(from_chain_id)
        else:
            self.provider = provider

        if is_chain_supported(from_chain_id) is False:
            raise Exception(f"Origin Chain ID {from_chain_id} not supported: add it to the config.json file or open a request to add it.")
        if is_chain_supported(to_chain_id) is False:
            raise Exception(f"Destination Chain ID {to_chain_id} not supported: add it to the config.json file or open a request to add it.")

        if self.l1_to_l2:
            self.address = read_addresses(from_chain_id, to_chain_id, layer="l1")["L1_STANDARD_BRIDGE"]
        else:
            self.address = read_addresses(to_chain_id, from_chain_id, layer="l2")["L2_STANDARD_BRIDGE"]
        
        self.from_chain_id = from_chain_id
        self.to_chain_id = to_chain_id

        self.account = account

        if self.l1_to_l2:
            self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L1_STANDARD_BRIDGE"))
        else:
            self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L2_STANDARD_BRIDGE"))
    
    def deposit_eth_to(self, to, value, gas_limit, extra_data):

        if not self.l1_to_l2:
            raise Exception("This method can only be called on a L1 to L2 Bridge")

        deposit_eth_to_tx = self.contract.functions.depositETHTo(to, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": value
        })

        return self.sign_and_broadcast(deposit_eth_to_tx)

    def deposit_erc20(self, l1_token_address, l2_token_address, value, gas_limit, extra_data):
        
        if not self.l1_to_l2:
            raise Exception("This method can only be called on a L1 to L2 Bridge")
        
        deposit_erc20_tx = self.contract.functions.depositERC20(l1_token_address, l2_token_address, value, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": 700000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address)
        })

        return self.sign_and_broadcast(deposit_erc20_tx)
        
    def deposit_erc20_to(self, l1_token_address, l2_token_address, to, value, gas_limit, extra_data):
        
        if not self.l1_to_l2:
            raise Exception("This method can only be called on a L1 to L2 Bridge")
        
        deposit_erc20_to_tx = self.contract.functions.depositERC20To(l1_token_address, l2_token_address, to, value, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": 700000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address)
        })

        return self.sign_and_broadcast(deposit_erc20_to_tx)
        

    def withdraw_eth_to(self, to, value, gas_limit, extra_data):

        if self.l1_to_l2:
            raise Exception("This method can only be called on a L2 to L1 Bridge")
        
        withdraw_eth_to_tx = self.contract.functions.withdrawTo("0xDeadDeAddeAddEAddeadDEaDDEAdDeaDDeAD0000", to, value, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": value
        })

        return self.sign_and_broadcast(withdraw_eth_to_tx)
    
    def bridge_erc20(self, l1_token_address, l2_token_address, value, gas_limit, extra_data):

        if self.l1_to_l2:
            raise Exception("This method can only be called on a L2 to L1 Bridge")
        
        withdraw_erc20_tx = self.contract.functions.bridgeERC20(l2_token_address, l1_token_address, value, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address)
        })

        return self.sign_and_broadcast(withdraw_erc20_tx)

    def bridge_erc20_to(self, l1_token_address, l2_token_address, to, value, gas_limit, extra_data):
        
        if self.l1_to_l2:
            raise Exception("This method can only be called on a L2 to L1 Bridge")
        
        withdraw_erc20_to_tx = self.contract.functions.bridgeERC20To(l2_token_address, l1_token_address, to, value, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address)
        })

class CrossChainMessengerContract(Contract):

    def __init__(self, account, from_chain_id=1, to_chain_id=10, provider=None):

        self.l1_to_l2 = determine_direction(from_chain_id, to_chain_id)

        if provider is None:
            self.provider = get_provider(chain_id=from_chain_id)
        else:
            self.provider = provider

        if is_chain_supported(from_chain_id) is False:
            raise Exception(f"Origin Chain ID {from_chain_id} not supported: add it to the config.json file or open a request to add it.")
        if is_chain_supported(to_chain_id) is False:
            raise Exception(f"Destination Chain ID {to_chain_id} not supported: add it to the config.json file or open a request to add it.")

        if self.l1_to_l2:
            self.address = read_addresses(from_chain_id, to_chain_id, layer="l1")["L1_CROSS_CHAIN_MESSENGER"]
        else:
            self.address = read_addresses(to_chain_id, from_chain_id, layer="l2")["L2_CROSS_CHAIN_MESSENGER"]
        
        self.from_chain_id = from_chain_id
        self.to_chain_id = to_chain_id

        self.account = account

        if self.l1_to_l2:
            self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L1_CROSS_MESSENGER"))
        else:
            self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L2_CROSS_MESSENGER"))


    def send_message(self, target, message, min_gas_limit, value=None):

        send_message_tx = self.contract.functions.sendMessage(target, message, min_gas_limit).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": 0 if value is None else value
        })

        return self.sign_and_broadcast(send_message_tx)
    
    def message_nonce(self):

        return self.contract.functions.messageNonce().call()

    
class L2OutputOracle():

    def __init__(self, chain_id_l1, chain_id_l2, account, provider=None):
            
        if provider is None:
            self.provider = get_provider(chain_id_l1)
        else:
            self.provider = provider

        if is_chain_supported(chain_id_l1) is False:
            raise Exception(f"Chain ID {chain_id_l1} not supported: add it to the config.json file or open a request to add it.")
        if is_chain_supported(chain_id_l2) is False:
            raise Exception(f"Chain ID {chain_id_l2} not supported: add it to the config.json file or open a request to add it.")
    
        self.address = read_addresses(chain_id_l1, chain_id_l2, layer="l1")["L2_OUTPUT_ORACLE"]

        self.account = account

        self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L2_OUTPUT_ORACLE"))

    def latest_output_index(self):

        return self.contract.functions.latestOutputIndex().call()
    
    def latest_block_number(self):

        return self.contract.functions.latestBlockNumber().call()

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
    
class L2ToL1MessagePasser(Contract):

    def __init__(self, chain_id_l1, chain_id_l2, account, provider=None):

        if provider is None:
            self.provider = get_provider(chain_id_l2)
        else:
            self.provider = provider

        self.address = read_addresses(chain_id_l1, chain_id_l2, layer="l2")["L2_TO_L1_MESSAGE_PASSER"]

        self.account = account

        self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L2_TO_L1_MESSAGE_PASSER"))

    def initiate_withdrawl(self, to, gas_limit, data, value):

        initiate_withdrawl_tx = self.contract.functions.initiateWithdrawal(to, gas_limit, data).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": value
        })

        return self.sign_and_broadcast(initiate_withdrawl_tx)