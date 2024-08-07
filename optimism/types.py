from enum import Enum

class MessageStatus(Enum):
    UNCONFIRMED_L1_TO_L2_MESSAGE = 0
    UNCONFIRMED_L2_TO_L1_MESSAGE = 1
    FAILED_L1_TO_L2_MESSAGE = 2
    FAILED_L2_TO_L1_MESSAGE = 3
    STATE_ROOT_NOT_PUBLISHED = 4
    READY_TO_PROVE = 5
    IN_CHALLENGE_PERIOD = 6
    READY_FOR_RELAY = 7
    RELAYED = 8

class ChainInfo:
    def __init__(self, chain_id, layer):
        self.chain_id = chain_id
        self.layer = layer

class Chains(Enum):
    ETHEREUM_MAINNET = ChainInfo(1, 'L1')
    OPTIMISM_MAINNET = ChainInfo(10, 'L2')
    BASE_MAINNET = ChainInfo(8453, 'L2')

    ETHEREUM_SEPOLIA = ChainInfo(11155111, 'L1')
    OPTIMISM_SEPOLIA = ChainInfo(11155420, 'L2')
    BASE_SEPOLIA = ChainInfo(84532, 'L2')

    def chain_id(self):
        return self.value.chain_id

    def layer(self):
        return self.value.layer

class StateTrieProof():

    def __init__(self, account_proof, storage_proof, storage_value, storage_root):
        
        self.account_proof = account_proof
        self.storage_proof = storage_proof
        self.storage_value = storage_value
        self.storage_root = storage_root

    def __str__(self):

        return f"StateTrieProof(account_proof={self.account_proof}, storage_proof={self.storage_proof}, storage_value={self.storage_value}, storage_root={self.storage_root})"
    
class MessagePassedEvent():

    def __init__(self, message_nonce, sender, target, value, min_gas_limit, message):
        
        self.message_nonce = message_nonce
        self.sender = sender
        self.target = target
        self.value = value
        self.min_gas_limit = min_gas_limit
        self.message = message
    
    def __str__(self):

        return f"MessagePassedEvent(message_nonce={self.message_nonce}, sender={self.sender}, target={self.target}, value={self.value}, min_gas_limit={self.min_gas_limit}, message={self.message})"
    
    def values(self):

        return (self.message_nonce, self.sender, self.target, self.value, self.min_gas_limit, self.message)

class OutputRootProof():

    def __init__(self, version, state_root, message_passer_storage_root, latest_blockhash):

        self.version = version
        self.state_root = state_root
        self.message_passer_storage_root = message_passer_storage_root
        self.latest_blockhash = latest_blockhash

    def __str__(self):

        return f"OutputRootProof(version={self.version}, state_root={self.state_root}, message_passer_storage_root={self.message_passer_storage_root}, latest_blockhash={self.latest_blockhash})"
    
    def values(self):

        return (self.version, self.state_root, self.message_passer_storage_root, self.latest_blockhash)


class BedrockMessageProof():

    def __init__(self, output_root_proof, withdrawl_proof, dispute_game_index):

        self.output_root_proof = output_root_proof
        self.withdrawl_proof = withdrawl_proof
        self.dispute_game_index = dispute_game_index

    def __str__(self):
            
        return f"BedrockMessageProof(output_root_proof={self.output_root_proof}, withdrawl_proof={self.withdrawl_proof}, dispute_game_index={self.dispute_game_index})"
    
    def get_dispute_game_index(self):

        return self.dispute_game_index
    
    def get_output_root_proof(self):

        return self.output_root_proof.values()
    
    def get_withdrawl_proof(self):

        return tuple(self.withdrawl_proof)
