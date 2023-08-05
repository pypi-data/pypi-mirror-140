
## Install Packages
```
pip install hashflow-python
```

## Example Usage
### Initialize the client
```python
from hashflow.client import Client

# create a new client with a private key (string or bytearray)
hflow = Client(
    private_key='0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d',
    network_id = 1,
    node='https://mainnet.infura.io/v3/00000000000000000000000000000000'
)
```
### Interacting with the protocol
```python
# set eip 1559 gas fees. in options. Nonce is optional and only needed if resubmitting a tx.
options = { 'maxFeePerGas' : 500000000000, 'maxPriorityFeePerGas': 5000000000, 'nonce': 11}
# create a new hashflow pool
  hflow.main.factory.create_pool(name='hash42', signer=signer, admin=admin, options=options)

# fetch pool addresses deployed using operations key
  hflow.main.factory.pools(operations, options)

# set hashflow allowance
hflow.main.erc20.set_maximum_allowance(token, options)

# check allowance
hflow.main.erc20.allowance(token, owner,spender, options)

# To add Eth liquidity set token address to zero address 
hflow.main.router.add_liquidity_private_pool(pool, token, amount, options)
hflow.main.router.add_liquidity_public_pool(pool, token, amount, options)

# Optionally pass binance account address to transfer funds directly
hflow.main.router.remove_liquidity_private_pool(pool, token, amount, recipient=binance, options)
# To remove liquidity from public pools LPs must burn native h-tokens
hflow.main.router.remove_liquidity_public_pool(pool, token, burn_amount, options)

# Transfer assets to CeFi venues to rebalance
hflow.main.pool.transfer_assets(pool, token, recipient, amount, options)


# generate quote 
quote = utils.Quote(pool,eoa, trader, effective_trader, base_token_address, quote_token_address, base_token_amount, quote_token_amount, fees, expiry, flag, txid, k_value, trade_eoa)

# hash quote 
quote_digest = hflow.main.hash_quote(quote)

# hash quote for EOA
quote_digest = hflow.main.hash_quote_eoa(quote)

# sign quote
signed_quote = utils.sign_digest(quote_digest, signer_private_key)

# trade 
#effective_base_token_amount is optional arg if you wanna do routing.
hflow.main.router.trade_single_hop(quote, signed_quote, effective_base_token_amount, options)

```

