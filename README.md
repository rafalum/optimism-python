# Optimism-Python: Unofficial Python Client for the OP-Stack

#### :construction: **DISCLAIMER**: Reference SDK is still under active development so the repository might be temporarily out of date.

<div align="center">
    <img src="https://github.com/rafalum/optimism-python/assets/38735195/12cb4de6-7cb5-403d-993b-5461febd5b72" width=200 height=200 />
</div>


This library is a Python implementation of the [OP-Stack SDK](https://sdk.optimism.io/). It tries to mirror some of the core functionalities such as:

- providing easy access to the OP-Stack contracts
- bridging of assets from L1 to L2 (deposits) and vice-versa (withdrawls)
- creating withdrawl proofs

## Getting started

### Installation

```bash
pip install optimism-python
```

### Deposit ETH to L2

```python
from web3 import Web3
from optimism import CrossChainMessenger

# Create a node provider for each chain
provider_l1 = Web3(Web3.HTTPProvider("https://eth-mainnet.g.alchemy.com/v2/<your-alchemy-key>"))
provider_l2 = Web3(Web3.HTTPProvider("https://optimism-mainnet.g.alchemy.com/v2/<your-alchemy-key>"))

# Specify an account for each chain (can be the same)
account_l1 = provider_l1.eth.account.from_key("<your-private-key>")
account_l2 = provider_l2.eth.account.from_key("<your-private-key>")

# Create a messenger instance
messenger = CrossChainMessenger(chain_id_l1=1,          # Ethereum Mainnet
                                chain_id_l2=10,         # Optimism Mainnet
                                account_l1=account_l1, 
                                account_l2=account_l2,
                                provider_l1=provider_l1,
                                provider_l2=provider_l2)

# Deposit 1 ETH to L2
messenger.deposit_eth(10**18)
```
