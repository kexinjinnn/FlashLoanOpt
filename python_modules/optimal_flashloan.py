from web3 import Web3
import time
import numpy as np
from web3 import Web3
from common import *
from get_reserve import *
from get_gasfee import print_gas_price
from get_optimal_profit import get_optimal_ex_amount_a

# to ensure the below queries don't return stale values

def optimal_flashloan(check_interval=1): # in seconds
    while True:
        print('================================ Trial =================================')
        gasfee = print_gas_price()
        ex_direction, ex_amount_a, profit_in_a = get_optimal_ex_amount_a()
        print('Exchange direction: ', ex_direction)
        print('Optimal exchange amount of a: ', ex_amount_a)
        flashloan_gasfee = gasfee * 0.001 # this is approximation fee for flashloan (unit Gerlieth)
        eth2wbtc = get_eth_price() # rate of eth to wbtc
        flashloan_gasfee_wbtc = flashloan_gasfee * eth2wbtc # this is approximation fee for flashloan (unit Gerlieth)
        print("gas fee: {}".format(flashloan_gasfee_wbtc))
        predict_profit_minus_fee = profit_in_a - flashloan_gasfee_wbtc
        if predict_profit_minus_fee > 0:
            print('Predicted profit: ', predict_profit_minus_fee)
            if ex_direction == 'wbtc_to_aux_on_uni': # flashloan wbtc and trade on uni first
                w3 = Web3(Web3.HTTPProvider(RPC_URL))
                public_address = w3.eth.account.from_key(PRIVATE_KEY).address
                flash_loan_arbitrage_contract = w3.eth.contract(address=FLASH_LOAN_ARBITRAGE_ADDRESS, abi=FLASH_LOAN_ARBITRAGE_ABI)
                txn = flash_loan_arbitrage_contract.functions.arbitrage(WBTC_ADDRESS, AUX_ADDRESS, int(ex_amount_a * 10**8), 1, 0).build_transaction({'nonce':w3.eth.get_transaction_count(public_address),'from': public_address})
                txn_signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
                txn_hash = w3.eth.send_raw_transaction(txn_signed.rawTransaction)
                w3.eth.wait_for_transaction_receipt(txn_hash)
                time.sleep(10) 
            else: # flashloan aux and trade on sushi first
                w3 = Web3(Web3.HTTPProvider(RPC_URL))
                public_address = w3.eth.account.from_key(PRIVATE_KEY).address
                flash_loan_arbitrage_contract = w3.eth.contract(address=FLASH_LOAN_ARBITRAGE_ADDRESS, abi=FLASH_LOAN_ARBITRAGE_ABI)
                txn = flash_loan_arbitrage_contract.functions.arbitrage(WBTC_ADDRESS, AUX_ADDRESS, int(ex_amount_a * 10**8), 0, 1).build_transaction({'nonce':w3.eth.get_transaction_count(public_address),'from': public_address})
                txn_signed = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
                txn_hash = w3.eth.send_raw_transaction(txn_signed.rawTransaction)
                w3.eth.wait_for_transaction_receipt(txn_hash)
                time.sleep(10) 
            break

        time.sleep(check_interval)



if __name__ == "__main__":
    optimal_flashloan()