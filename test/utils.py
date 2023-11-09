

class TestUtil():

    def __init__(self) -> None:
        pass

    def fund_account(self, account, value):
        
        tx = {
            'nonce': self.l1_provider.eth.get_transaction_count(self.faucet.address),
            'to': account.address,
            'value': value,
            'gas': 50000, 
            'gasPrice': self.l1_provider.eth.gas_price
        }

        # Sign the transaction
        signed_tx = self.l1_provider.eth.account.sign_transaction(tx, self.faucet.key)
        tx_hash = self.l1_provider.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.l1_provider.eth.wait_for_transaction_receipt(tx_hash)

        return tx_hash.hex(), receipt