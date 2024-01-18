# On-chain DEX slippage evaluator
for Morpho Blue

## Description
Compute for a given Morpho Blue market (collateral token, loan token and LLTV) the maximum amount of token which can be used to make a borrower at LTV=LLTV creates bad debt through on-chain slippage.

## Requirements

- You should set a Node Provider URL in your $RPC_URL environment variable
  
``
export RPC_URL=<Provider_URL>
``
- You should set a 1Inch Dev API Key in your $ONEINCH_API_KEY environment variable
  
``
export ONEINCH_API_KEY=<API_KEY>
``
- You should install the required modules from requirements.txt
  
``
pip -r install requirements.txt
``

- You should have Python > 3.8

## How to run

``
python predict_slippage.py 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 0.95
``
## Example 
``````
python predict_slippage.py 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 0.95

Sorry I am a bit slow to load, please wait one or two minutes

Amount to cause 3.5532994923857752% slippage on wstETH/WETH:

 67.0K wstETH = 194.0M USD
``````