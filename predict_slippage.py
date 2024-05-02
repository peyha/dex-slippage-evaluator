import requests
import json
import sys
import os
import time

from web3 import Web3

BASE_CHAIN_ID = 8453
ETHEREUM_CHAIN_ID = 1

chain_id_to_usdc = {
    ETHEREUM_CHAIN_ID: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    BASE_CHAIN_ID: '"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
}


def number_to_readable(num):
    ''' Convert a number to a readable format
    (e.g. 1000 -> 1K, 1000000 -> 1M)'''

    if num < 1000:
        return str(num)
    elif num < 1000000:
        return f"{num/1000:.1f}K"
    elif num < 1000000000:
        return f"{num/1000000:.1f}M"
    elif num < 1000000000000:
        return f"{num/1000000000:.1f}B"
    else:
        return f"{num/1000000000000:.1f}T"


def get_erc20_info(token_address, w3):
    ''' Get total supply, decimal and symbol of an ERC20 token '''

    with open('abis/ERC20_abi.json') as f:
        erc20_abi = json.load(f)
    token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)

    total_supply = token_contract.functions.totalSupply().call()
    decimal = token_contract.functions.decimals().call()
    symbol = token_contract.functions.symbol().call()

    return total_supply, decimal, symbol


def get_amount_out(amount_in, token_in, token_out, api_key, chain_id):
    ''' Get onchain amount out given amount in and token addresses
     using 1inch Routing API'''

    api_url = f"https://api.1inch.dev/swap/v5.2/{chain_id}/quote"

    # Prepare request components
    headers = {
        "Authorization": "Bearer " + api_key,
    }
    params = {
        "src": token_in,
        "dst": token_out,
        "amount": str(amount_in),
    }

    response = requests.get(api_url, headers=headers, params=params)
    try:
        amount_out = int(response.json()['toAmount'])
    except:
        raise ValueError(f"API error: {response.text}")

    return amount_out


def get_onchain_price(token_in, decimal_in, api_key, chain_id):
    ''' Get onchain price of a token in USD 
    using 1inch Routing API by swapping 1 token for USDC'''

    token_out, decimal_out = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 6  # USDC

    amount_out = get_amount_out(
        1 * 10**decimal_in, token_in, token_out, api_key, chain_id)
    price = amount_out / 10**decimal_out

    return price


def predict_slippage(percentage, token_in, decimal_in, total_supply_in, token_out, decimal_out, api_key, chain_id):
    ''' Predict the amount of token_in needed to cause a certain slippage
    percentage on token_in/token_out pair using 1inch Routing API'''

    amount_in = 1 ** 10**decimal_in
    amount_out = get_amount_out(
        amount_in, token_in, token_out, api_key, chain_id)
    initial_price = amount_out / amount_in  # reference price

    amount_left = 1 * 10**decimal_in
    amount_right = total_supply_in

    # Binary search
    N_iter = 10
    for _ in range(N_iter):
        amount_mid = (amount_left + amount_right) // 2

        # Sleep to prevent API spamming
        time.sleep(1.5)
        amount_out = get_amount_out(
            amount_mid, token_in, token_out, api_key, chain_id)

        price_ratio = amount_out / amount_mid / \
            initial_price  # current_price / price_reference
        if price_ratio > percentage:
            amount_left = amount_mid
        else:
            amount_right = amount_mid

    return amount_left


if __name__ == '__main__':

    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print(
            'Usage: python predict_slippage.py token_in token_out lltv [chain]')
        sys.exit(1)
    print("Sorry I am a bit slow to load, please wait one or two minutes")

    # Example:
    # python predict_slippage.py 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 0.95

    token_in = '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'  # wsteth
    token_out = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'  # weth
    lltv = 0.95

    token_in = Web3.to_checksum_address(sys.argv[1])
    token_out = Web3.to_checksum_address(sys.argv[2])
    lltv = float(sys.argv[3])
    if len(sys.argv) == 4:
        chain_id = ETHEREUM_CHAIN_ID
    elif len(sys.argv) == 5:
        assert sys.argv[4] in ['ethereum', 'base']
        chain_id = ETHEREUM_CHAIN_ID if sys.argv[4] == 'ethereum' else BASE_CHAIN_ID

    api_key = os.environ['ONEINCH_API_KEY']
    w3 = Web3(Web3.HTTPProvider(os.environ['RPC_URL']))

    with open('abis/ERC20_abi.json') as f:
        erc20_abi = json.load(f)
    token_in_contract = w3.eth.contract(address=token_in, abi=erc20_abi)
    token_out_contract = w3.eth.contract(address=token_out, abi=erc20_abi)

    total_supply_in, decimal_in, symbol_in = get_erc20_info(token_in, w3)
    total_supply_out, decimal_out, symbol_out = get_erc20_info(token_out, w3)

    m, beta = 1.15, 0.3
    lif = min(m, 1 / (beta * lltv + (1 - beta)))
    critical_ltv = 1 / lif
    p = lltv / critical_ltv

    amount_slippage = predict_slippage(
        p, token_in, decimal_in, total_supply_in, token_out, decimal_out, api_key, chain_id)

    time.sleep(1.5)
    price = get_onchain_price(token_in, decimal_in, api_key, chain_id)
    amount_slippage_usd = amount_slippage * price / 10**decimal_in

    print(f'Amount to cause {(1-p)*100}% slippage on {symbol_in}/{symbol_out}:\n' +
          f'\r {number_to_readable(amount_slippage / 10**decimal_in)} {symbol_in} = ' +
          f'{number_to_readable(amount_slippage_usd)} USD')
