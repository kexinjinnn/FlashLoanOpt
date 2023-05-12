from web3 import Web3
import time
from common import *

# Returns the live quotes from the Uniswap and SushiSwap pool contracts
def get_reserves(verbose=True):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    # Setup contracts
    wbtc_contract = w3.eth.contract(address=WBTC_ADDRESS, abi=ERC20_ABI)
    aux_contract = w3.eth.contract(address=AUX_ADDRESS, abi=ERC20_ABI)
    uniswap_pool_contract = w3.eth.contract(address=UNISWAP_POOL_ADDRESS, abi=UNISWAP_V2_PAIR_ABI)
    sushiswap_pool_contract = w3.eth.contract(address=SUSHISWAP_POOL_ADDRESS, abi=UNISWAP_V2_PAIR_ABI)

    # Fetch token decimals
    wbtc_decimals = wbtc_contract.functions.decimals().call()
    aux_decimals = aux_contract.functions.decimals().call()

    uniswap_wbtc_amount, uniswap_aux_amount, _ = uniswap_pool_contract.functions.getReserves().call()
    sushiswap_wbtc_amount, sushiswap_aux_amount, _ = sushiswap_pool_contract.functions.getReserves().call()

    uniswap_aux_reserve = uniswap_aux_amount / 10**aux_decimals
    uniswap_wbtc_reserve = uniswap_wbtc_amount / 10**wbtc_decimals
    sushiswap_aux_reserve = sushiswap_aux_amount / 10**aux_decimals
    sushiswap_wbtc_reserve = sushiswap_wbtc_amount / 10**wbtc_decimals
    if verbose:
        print("Uniswap "+ AUX_TOKEN +" reserve: ", uniswap_aux_reserve)
        print("Uniswap wBTC reserve: ", uniswap_wbtc_reserve)
        print("SushiSwap "+ AUX_TOKEN +" reserve: ", sushiswap_aux_reserve)
        print("SushiSwap wBTC reserve: ", sushiswap_wbtc_reserve)
    return uniswap_aux_reserve, uniswap_wbtc_reserve, sushiswap_aux_reserve, sushiswap_wbtc_reserve

def get_eth_price(verbose=False):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    # Setup contracts
    wbtc_contract = w3.eth.contract(address=WBTC_ADDRESS, abi=ERC20_ABI)
    eth_contract = w3.eth.contract(address=ETH_ADDRESS, abi=ERC20_ABI)
    sushiswap_pool_contract = w3.eth.contract(address=SUSHISWAP_ETH_POOL_ADDRESS, abi=UNISWAP_V2_PAIR_ABI)

    # Fetch token decimals
    wbtc_decimals = wbtc_contract.functions.decimals().call()
    eth_decimals = eth_contract.functions.decimals().call()

    sushiswap_wbtc_amount, sushiswap_eth_amount, _ = sushiswap_pool_contract.functions.getReserves().call()

    sushiswap_eth_reserve = sushiswap_eth_amount / 10**eth_decimals
    sushiswap_wbtc_reserve = sushiswap_wbtc_amount / 10**wbtc_decimals

    sushiswap_wbtc_over_eth = sushiswap_wbtc_reserve / sushiswap_eth_reserve

    if verbose:
        print("SushiSwap GoerliETH reserve: ", sushiswap_eth_reserve)
        print("SushiSwap wBTC reserve: ", sushiswap_wbtc_reserve)
        print("SushiSwap wBTC/ETH exchange rate: ", sushiswap_wbtc_over_eth)
    return sushiswap_wbtc_over_eth 
    

def get_prices(verbose=True):
    uniswap_aux_reserve, uniswap_wbtc_reserve, sushiswap_aux_reserve, sushiswap_wbtc_reserve = get_reserves()
    # aux/wbtc exchange rate
    uniswap_aux_over_wbtc = uniswap_aux_reserve / uniswap_wbtc_reserve
    sushiswap_aux_over_wbtc = sushiswap_aux_reserve / sushiswap_wbtc_reserve

    if verbose:
        print(AUX_TOKEN + "/wBTC exchange rate for Uniswap pool: {}".format(uniswap_aux_over_wbtc))
        print(AUX_TOKEN + "/wBTC exchange rate for SushiSwap pool: {}".format(sushiswap_aux_over_wbtc))

    return uniswap_aux_over_wbtc, sushiswap_aux_over_wbtc

if __name__ == "__main__":
    # uniswap_aux_reserve, uniswap_wbtc_reserve, sushiswap_aux_reserve, sushiswap_wbtc_reserve = get_reserves()
    # uniswap_aux_over_wbtc, sushiswap_aux_over_wbtc = get_prices()
    eth_price = get_eth_price(verbose=True)
