from web3 import Web3

from .addresses import *
from .constants import OUTPUT_ROOT_PROOF_VERSION
from .utils import get_provider, load_abi, determine_direction, to_low_level_message, hash_message_hash, make_state_trie_proof

class Contract():

    def __int__():
        pass

    def sign_and_broadcast(self, transaction):
        signed_txn = self.provider.eth.account.sign_transaction(transaction, self.account.key)
        txn_hash = self.provider.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = self.provider.eth.wait_for_transaction_receipt(txn_hash)

        return txn_hash.hex(), txn_receipt
    
class OptimismPortal(Contract):

    def __init__(self, account, provider=None, network="mainnet"):
        
        if provider is None:
            self.provider = get_provider(network=network)
        else:
            self.provider = provider

        if network == "mainnet":
            self.address = OPTIMISM_PORTAL
        elif network == "goerli":
            self.address = OPTIMISM_PORTAL_GOERLI
        elif network == "sepolia":
            self.address = OPTIMISM_PORTAL_SEPOLIA
        
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

class StandardBridge(Contract):
    
    def __init__(self, account, from_chain_id=1, to_chain_id=10, provider=None, network="mainnet"):
        
        l1_to_l2 = determine_direction(from_chain_id, to_chain_id)
        l2 = not l1_to_l2

        if provider is None:
            self.provider = get_provider(l2=l2, network=network)
        else:
            self.provider = provider

        if l1_to_l2:
            if network == "mainnet":
                self.address = L1_STANDARD_BRIDGE
            elif network == "goerli":
                self.address = L1_STANDARD_BRIDGE_GOERLI
            elif network == "sepolia":
                self.address = L1_STANDARD_BRIDGE_SEPOLIA
        else:
            if network == "mainnet":
                self.address = L2_STANDARD_BRIDGE
            elif network == "goerli":
                self.address = L2_STANDARD_BRIDGE_GOERLI
            elif network == "sepolia":
                self.address = L2_STANDARD_BRIDGE_SEPOLIA
        
        self.from_chain_id = from_chain_id
        self.to_chain_id = to_chain_id

        self.account = account

        if l1_to_l2:
            self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L1_STANDARD_BRIDGE"))
        else:
            self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L2_STANDARD_BRIDGE"))

    def bridge_eth():
        pass
    
    def deposit_eth_to(self, to, gas_limit, extra_data, value):
        
        deposit_eth_to_tx = self.contract.functions.depositETHTo(to, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": value
        })

        return self.sign_and_broadcast(deposit_eth_to_tx)

    def bridge_erc20():
        pass

    def withdraw_eth_to(self, to, amount, gas_limit, extra_data):
        
        withdraw_eth_to_tx = self.contract.functions.withdrawTo("0xDeadDeAddeAddEAddeadDEaDDEAdDeaDDeAD0000", to, amount, gas_limit, extra_data).build_transaction({
            "from": self.account.address,
            "gas": 500000,
            "nonce": self.provider.eth.get_transaction_count(self.account.address),
            "value": amount
        })

        return self.sign_and_broadcast(withdraw_eth_to_tx)

    def bridge_erc20_to():
        pass

class CrossChainMessenger(Contract):

    def __init__(self, account, from_chain_id=1, to_chain_id=10, provider=None, network="mainnet"):

        self.l1_to_l2 = determine_direction(from_chain_id, to_chain_id)
        l2 = not self.l1_to_l2

        if provider is None:
            self.provider = get_provider(l2=l2, network=network)
        else:
            self.provider = provider

        if self.l1_to_l2:
            if network == "mainnet":
                self.address = L1_CROSS_CHAIN_MESSENGER
            elif network == "goerli":
                self.address = L1_CROSS_CHAIN_MESSENGER_GOERLI
            elif network == "sepolia":
                self.address = L1_CROSS_CHAIN_MESSENGER_SEPOLIA
        else:
            if network == "mainnet":
                self.address = L2_CROSS_CHAIN_MESSENGER
            elif network == "goerli":
                self.address = L2_CROSS_CHAIN_MESSENGER_GOERLI
            elif network == "sepolia":
                self.address = L2_CROSS_CHAIN_MESSENGER_SEPOLIA
        
        self.from_chain_id = from_chain_id
        self.to_chain_id = to_chain_id

        self.network = network
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
    
    def deposit_eth(self, value):

        if not self.l1_to_l2:
            raise Exception("Cannot deposit ETH to L1: Instantiate a L2CrossChainMessenger and call withdraw_eth_to()")
        
        return self.send_message(self.account.address, b"", 0, value)

    def withdraw_eth(self, value):
        
        if self.l1_to_l2:
            raise Exception("Cannot withdraw ETH to L2: Instantiate a L1CrossChainMessenger and call deposit_eth_to()")
        
        l2_to_l1_message_passer = L2ToL1MessagePasser(self.account, network=self.network)
        
        return l2_to_l1_message_passer.initiate_withdrawl(self.account.address, 0, b"", value)

    def wait_for_message_status(self):
        pass
    
    def prove_message(self, l2_txn_hash, account_l1=None):

        if self.l1_to_l2:
            raise Exception("Cannot prove message on L1CrossChainMessenger: Instantiate a L2CrossChainMessenger")
        
        if account_l1 is None:
            account_l1 = self.account
        
        l2_txn = self.provider.eth.get_transaction(l2_txn_hash)
        l2_txn_receipt = self.provider.eth.get_transaction_receipt(l2_txn_hash)

        withdrawl_message, withrawl_message_hash = to_low_level_message(l2_txn, l2_txn_receipt)
        proof = self._get_bedrock_message_proof(l2_txn, withrawl_message_hash, account_l1)

        optimism_portal = OptimismPortal(account_l1, network=self.network)
        return optimism_portal.prove_withdrawl_transaction(tuple(withdrawl_message.values()), proof["l2OutputIndex"], tuple(proof["outputRootProof"].values()), tuple(proof["withdrawalProof"]))
    
    def finalize_message(self, l2_txn_hash, account_l1=None):
        
        if self.l1_to_l2:
            raise Exception("Cannot finalize message on L1CrossChainMessenger: Instantiate a L2CrossChainMessenger")
        
        if account_l1 is None:
            account_l1 = self.account

        l2_txn = self.provider.eth.get_transaction(l2_txn_hash)
        l2_txn_receipt = self.provider.eth.get_transaction_receipt(l2_txn_hash)

        withdrawl_message, withrawl_message_hash = to_low_level_message(l2_txn, l2_txn_receipt)
        
        optimism_portal = OptimismPortal(self.account, network=self.network)
        return optimism_portal.finalize_withdrawl_transaction(tuple(withdrawl_message.values()))


    def _get_bedrock_message_proof(self, txn, withdrawl_hash, account_l1):

        l2_block_number = txn.blockNumber

        l2_output_oracle = L2OutputOracle(account_l1, network=self.network)

        latest_l2_output_index = l2_output_oracle.latest_output_index()
        output_root, timestamp, l2_block_number = l2_output_oracle.get_l2_output(latest_l2_output_index)

        message_slot = hash_message_hash(withdrawl_hash)

        state_trie_proof = make_state_trie_proof(self.provider, l2_block_number, L2_TO_L1_MESSAGE_PASSER, message_slot)

        block = self.provider.eth.get_block(l2_block_number)
        
        return {
            "outputRootProof": {
                "version": OUTPUT_ROOT_PROOF_VERSION,
                "stateRoot": block.stateRoot.hex(),
                "messagePasserStorageRoot": state_trie_proof["storage_root"].hex(),
                "latestBlockhash": block.hash.hex(),
            },
            "withdrawalProof": [el.hex() for el in state_trie_proof["storage_proof"]],
            "l2OutputIndex": latest_l2_output_index,
        }

    
class L2OutputOracle():

    def __init__(self, account, provider=None, network="mainnet"):
            
        if provider is None:
            self.provider = get_provider(network=network)
        else:
            self.provider = provider

        if network == "mainnet":
            self.address = L2_OUTPUT_ORACLE
        elif network == "goerli":
            self.address = L2_OUTPUT_ORACLE_GOERLI
        elif network == "sepolia":
            self.address = L2_OUTPUT_ORACLE_SEPOLIA

        self.account = account

        self.contract = self.provider.eth.contract(address=self.address, abi=load_abi("L2_OUTPUT_ORACLE"))

    def latest_output_index(self):

        return self.contract.functions.latestOutputIndex().call()

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

    def __init__(self, account, provider=None, network="mainnet"):

        if provider is None:
            self.provider = get_provider(l2=True, network=network)
        else:
            self.provider = provider

        if network == "mainnet":
            self.address = L2_TO_L1_MESSAGE_PASSER
        elif network == "goerli":
            self.address = L2_TO_L1_MESSAGE_PASSER_GOERLI
        elif network == "sepolia":
            self.address = L2_TO_L1_MESSAGE_PASSER_SEPOLIA

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