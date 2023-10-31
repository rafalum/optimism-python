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