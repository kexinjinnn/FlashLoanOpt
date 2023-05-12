#https://www.quicknode.com/guides/ethereum-development/transactions/estimating-gas-price-using-pending-transactions-in-python/

from web3 import Web3, HTTPProvider
import time
testnet = 'https://goerli.infura.io/v3/aa51429cd8064ebe9cacb8a5c61d36b0'
mainnet = 'https://mainnet.infura.io/v3/aa51429cd8064ebe9cacb8a5c61d36b0'

# Connect to the Goerli testnet using a provider
w3 = Web3(Web3.HTTPProvider(testnet))

def get_gas_price():
    return w3.eth.gas_price

def print_gas_price():
    gas_price = get_gas_price()
    gas_price_eth = gas_price*1e-9
    # gas_price_in_eth = w3.fromGwei(gas_price, 'ether')
    # print(f"Current gas price on Goerli testnet: {gas_price} Gwei")
    print(f"Current gas price on Goerli testnet: {gas_price_eth} eth")
    return gas_price_eth

def monitor_gas_price(interval):
    while True:
        print_gas_price()
        time.sleep(interval)

# def gas_estimation(tx):
#     # Your Ethereum address (sender)
#     YOUR_ADDRESS = "0xYourAddress"

#     # Flash loan contract information
#     CONTRACT_ADDRESS = "0xContractAddress"
#     CONTRACT_ABI = [...]  # Replace with the ABI of your deployed flash loan contract

#     # Connect to the contract
#     contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#     # Encode the function call for initiating the flash loan (use the appropriate function name and parameters)
#     function_name = "initiateFlashLoan"  # Replace with your contract's function name for initiating the flash loan
#     params = (AMOUNT, PARAM1, PARAM2)  # Replace with the required parameters for your function
#     ENCODED_FUNCTION_CALL = contract.encodeABI(fn_name=function_name, args=params)

#     transaction = {
#     'from': YOUR_ADDRESS,
#     'to': CONTRACT_ADDRESS,
#     'data': ENCODED_FUNCTION_CALL,
#     'value': 0
#     }

#     estimated_gas = w3.eth.estimateGas(transaction)


if __name__ == "__main__":
    monitor_interval = 1  # Time interval in seconds to check for updates
    monitor_gas_price(monitor_interval)