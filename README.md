# On-chain DEX slippage evaluator

for Morpho Blue

## Description

Compute for a given Morpho Blue market (collateral token, loan token and LLTV) the maximum amount of token which can be used to make a borrower at LTV=LLTV creates bad debt through on-chain slippage.

## Requirements

- You should set a Node Provider URL in your $RPC_URL environment variable. This RPC_URL should handle the specified chain.

`export RPC_URL=<Provider_URL>`

- You should set a 1Inch Dev API Key in your $ONEINCH_API_KEY environment variable

`export ONEINCH_API_KEY=<API_KEY>`

- You should install the required modules from requirements.txt

`pip -r install requirements.txt`

- You should have Python > 3.8

## How to run

`python predict_slippage.py <collateral_token_address> <loan_token_address> <lltv> [base|ethereum] `

## Example

On mainnet

```
python predict_slippage.py 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 0.95

Sorry I am a bit slow to load, please wait one or two minutes

Amount to cause 3.5532994923857752% slippage on wstETH/WETH:

 67.0K wstETH = 194.0M USD
```

On Base

'''
python predict_slippage.py 0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 0.95 base

Sorry I am a bit slow to load, please wait one or two minutes

Amount to cause 3.5532994923857752% slippage on wstETH/USDC:

126.70776811077683 wstETH = 436.1K USD
'''
