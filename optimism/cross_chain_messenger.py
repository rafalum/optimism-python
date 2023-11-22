from .constants import OUTPUT_ROOT_PROOF_VERSION, CHALLENGE_PERIOD_MAINNET, CHALLENGE_PERIOD_TESTNET

from .types import MessageStatus, OutputRootProof, BedrockMessageProof
from .utils import get_provider, get_account, to_low_level_message, make_state_trie_proof, hash_message_hash, read_addresses, load_abi
from .contracts import L2ToL1MessagePasser, L2OutputOracle, OptimismPortal, CrossChainMessengerContract, StandardBridge

class CrossChainMessenger():

    def __init__(self, chain_id_l1, chain_id_l2, account_l1=None, account_l2=None, provider_l1=None, provider_l2=None, network="mainnet"):

        if account_l1 is None:
            account_l1 = get_account(network=network)
        if account_l2 is None:
            account_l2 = get_account(l2=True, network=network)

        self.account_l1 = account_l1
        self.account_l2 = account_l2

        if provider_l1 is None:
            provider_l1 = get_provider(network=network)
        if provider_l2 is None:
            provider_l2 = get_provider(l2=True, network=network)

        self.provider_l1 = provider_l1
        self.provider_l2 = provider_l2

        self.chain_id_l1 = chain_id_l1
        self.chain_id_l2 = chain_id_l2

        self.network = network

        self.challenge_period = CHALLENGE_PERIOD_MAINNET if network == "mainnet" else CHALLENGE_PERIOD_TESTNET

        self.l1_cross_chain_messenger = CrossChainMessengerContract(account_l1, chain_id_l1, chain_id_l2, provider=provider_l1, network=network)
        self.l2_cross_chain_messenger = CrossChainMessengerContract(account_l2, chain_id_l2, chain_id_l1, provider=provider_l2, network=network)

        self.l1_bridge = StandardBridge(account_l1, from_chain_id=chain_id_l1, to_chain_id=chain_id_l2, provider=provider_l1, network=network)
        self.l2_bridge = StandardBridge(account_l2, from_chain_id=chain_id_l2, to_chain_id=chain_id_l1, provider=provider_l2, network=network)

    def deposit_eth(self, value):
        
        return self.l1_cross_chain_messenger.send_message(self.account_l2.address, b"", 0, value)
    
    def deposit_erc20(self, token_address_l1, token_address_l2, value):
        
        if not self._supports_token_pair(token_address_l1, token_address_l2):
            raise Exception("Token pair not supported")
        
        return self.l1_bridge.deposit_erc20(token_address_l1, token_address_l2, value, 0, b"")
    
    def deposit_erc20_to(self, token_address_l1, token_address_l2, to, value):
        
        if not self._supports_token_pair(token_address_l1, token_address_l2):
            raise Exception("Token pair not supported")
        
        return self.l1_bridge.deposit_erc20_to(token_address_l1, token_address_l2, to, value, 0, b"")

    def approve_erc20(self, token_address_l1, token_address_l2, value):

        if not self._supports_token_pair(token_address_l1, token_address_l2):
            raise Exception("Token pair not supported")

        token_contract_l1 = self.provider_l1.eth.contract(address=token_address_l1, abi=load_abi("ERC20"))

        approve_tx = token_contract_l1.functions.approve(self.l1_bridge.address, value).build_transaction({
            "from": self.account_l1.address,
            "nonce": self.provider_l1.eth.get_transaction_count(self.account_l1.address)
        })

        signed_txn = self.provider_l1.eth.account.sign_transaction(approve_tx, self.account_l1.key)
        txn_hash = self.provider_l1.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = self.provider_l1.eth.wait_for_transaction_receipt(txn_hash)

        return txn_hash.hex(), txn_receipt


    def withdraw_eth(self, value):
        
        l2_to_l1_message_passer = L2ToL1MessagePasser(self.account_l2, provider=self.provider_l2, network=self.network)
        
        return l2_to_l1_message_passer.initiate_withdrawl(self.account_l1.address, 0, b"", value)
    
    def withdraw_erc20(self, token_address_l1, token_address_l2, value):

        if not self._supports_token_pair(token_address_l1, token_address_l2):
            raise Exception("Token pair not supported")
        
        return self.l2_bridge.bridge_erc20(token_address_l1, token_address_l2, value, 0, b"")
    
    def withdraw_erc20_to(self, token_address_l1, token_address_l2, to, value):

        if not self._supports_token_pair(token_address_l1, token_address_l2):
            raise Exception("Token pair not supported")
            
        return self.l2_bridge.bridge_erc20_to(token_address_l1, token_address_l2, to, value, 0, b"")
    
    def prove_message(self, l2_txn_hash):
        
        l2_txn = self.provider_l2.eth.get_transaction(l2_txn_hash)
        l2_txn_receipt = self.provider_l2.eth.get_transaction_receipt(l2_txn_hash)

        withdrawl_message, withrawl_message_hash = to_low_level_message(l2_txn, l2_txn_receipt)
        message_proof = self.get_bedrock_message_proof(l2_txn, withrawl_message_hash)

        optimism_portal = OptimismPortal(self.account_l1, provider=self.provider_l1, network=self.network)
        return optimism_portal.prove_withdrawl_transaction(withdrawl_message.values(), message_proof.get_l2_output_index(), message_proof.get_output_root_proof(), message_proof.get_withdrawl_proof())
    
    def finalize_message(self, l2_txn_hash):

        l2_txn = self.provider_l2.eth.get_transaction(l2_txn_hash)
        l2_txn_receipt = self.provider_l2.eth.get_transaction_receipt(l2_txn_hash)

        withdrawl_message, withrawl_message_hash = to_low_level_message(l2_txn, l2_txn_receipt)
        
        optimism_portal = OptimismPortal(self.account_l1, provider=self.provider_l1, network=self.network)
        return optimism_portal.finalize_withdrawl_transaction(tuple(withdrawl_message.values()))


    def get_bedrock_message_proof(self, txn, withdrawl_hash):

        l2_block_number = txn.blockNumber

        l2_output_oracle = L2OutputOracle(self.account_l1, network=self.network)

        latest_l2_output_index = l2_output_oracle.latest_output_index()
        output_root, timestamp, l2_block_number = l2_output_oracle.get_l2_output(latest_l2_output_index)

        message_slot = hash_message_hash(withdrawl_hash)

        state_trie_proof = make_state_trie_proof(self.provider_l2, l2_block_number, read_addresses("l2")["l2_" + self.network]["L2_TO_L1_MESSAGE_PASSER"], message_slot)

        block = self.provider_l2.eth.get_block(l2_block_number)

        output_root_proof = OutputRootProof(version=OUTPUT_ROOT_PROOF_VERSION,
                                            state_root=block.stateRoot.hex(),
                                            message_passer_storage_root=state_trie_proof.storage_root.hex(),
                                            latest_blockhash=block.hash.hex())
        
        bedrock_message_proof = BedrockMessageProof(output_root_proof=output_root_proof,
                                                    withdrawl_proof=[el.hex() for el in state_trie_proof.storage_proof],
                                                    l2_output_index=latest_l2_output_index)
        
        return bedrock_message_proof
    
    def get_message_status(self, txn_hash):

        l1_to_l2 = True
        
        try:
            txn = self.provider_l1.eth.get_transaction(txn_hash)
            txn_receipt = self.provider_l1.eth.get_transaction_receipt(txn_hash)
        except:
            txn = self.provider_l2.eth.get_transaction(txn_hash)
            txn_receipt = self.provider_l2.eth.get_transaction_receipt(txn_hash)
            l1_to_l2 = False
        
        if l1_to_l2:
            if txn_receipt is None:
                return MessageStatus.UNCONFIRMED_L1_TO_L2_MESSAGE
            else:
                if txn_receipt.status == 1:
                    return MessageStatus.RELAYED
                else:
                    return MessageStatus.FAILED_L1_TO_L2_MESSAGE
        else:
            if txn_receipt is None:
                return MessageStatus.UNCONFIRMED_L2_TO_L1_MESSAGE
            else:
                if txn_receipt.status == 1:
                    l2_output_oracle = L2OutputOracle(self.account_l1, provider=self.provider_l1, network=self.network)
                    latest_block_number = l2_output_oracle.latest_block_number()

                    try:
                        _, message_hash = to_low_level_message(txn, txn_receipt)
                    except:
                        raise Exception("Transaction is not a valid L2 to L1 message")

                    if int(latest_block_number) < int(txn.blockNumber):
                        return MessageStatus.STATE_ROOT_NOT_PUBLISHED
                    else:
                        optimism_portal = OptimismPortal(self.account_l1, provider=self.provider_l1, network=self.network)
                        proven = optimism_portal.proven_withdrawls(message_hash)
                        if proven[-1] == 0:
                            return MessageStatus.READY_TO_PROVE
                        else:
                            current_timestamp = self.provider_l2.eth.get_block(self.provider_l2.eth.block_number).timestamp
                            if current_timestamp > proven[1] + self.challenge_period:
                                return MessageStatus.READY_FOR_RELAY
                            else:
                                return MessageStatus.IN_CHALLENGE_PERIOD
                else:
                    return MessageStatus.FAILED_L2_TO_L1_MESSAGE
    
    def get_deposits_by_address(self, address, from_block=0, to_block="latest"):
        raise NotImplementedError
    
    def get_withdrawls_by_address(self, address, from_block=0, to_block="latest"):
        raise NotImplementedError
    
    def estimate_l2_gas_limit(self, message):
        raise NotImplementedError
    
    def estimate_message_wait_time_seconds(self, message):
        raise NotImplementedError
    
    def get_challenge_period_seconds(self):
        raise NotImplementedError
    
    def get_proven_withdrawl(self):
        raise NotImplementedError
    
    def get_message_state_root(self):
        raise NotImplementedError
    
    def get_state_batch_appended_event_by_batch_index(self):
        raise NotImplementedError
    
    def get_state_batch_appended_event_by_transaction_index(self):
        raise NotImplementedError
    
    def get_state_root_batch_by_transaction_index(self):
        raise NotImplementedError
    
    def _supports_token_pair(self, token_address_l1, token_address_l2):
        
        token_contract_l2 = self.provider_l2.eth.contract(address=token_address_l2, abi=load_abi("OPTIMISM_ERC20"))
        try:
            l1_token = token_contract_l2.functions.l1Token().call()
        except:
            raise Exception(f"Token Contract {token_address_l2} is not an Optimism ERC20")
        
        return l1_token == token_address_l1