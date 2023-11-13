

class TestUtil():

    def __init__(self) -> None:
        pass

    def fund_account(self, account, value, layer="l1"):

        if layer == "l1":
            provider = self.l1_provider
        elif layer == "l2":
            provider = self.l2_provider
        else:
            raise Exception(f"Invalid layer: {layer}")
        
        tx = {
            'nonce': provider.eth.get_transaction_count(self.faucet.address),
            'to': account.address,
            'value': value,
            'gas': 50000, 
            'gasPrice': provider.eth.gas_price
        }

        # Sign and broadcast the transaction
        signed_tx = provider.eth.account.sign_transaction(tx, self.faucet.key)
        tx_hash = provider.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = provider.eth.wait_for_transaction_receipt(tx_hash)

        return tx_hash.hex(), receipt