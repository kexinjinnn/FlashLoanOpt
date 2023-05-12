from web3 import Web3
import time
import numpy as np
from common import *
from get_reserve import *

def predict_slippage(reserv_a, reserv_b, delta_a, ex_txn_fee=0.003):
    # predict the slippage of the price exchanging a for b by amount delta_a
    p_1 = reserv_b/reserv_a
    p_2 = (reserv_b - reserv_b/reserv_a*delta_a*(1-ex_txn_fee))/(reserv_a+delta_a)
    # print(p_1, p_2)
    price = 0.5*(p_1 + p_2)  # average before and after exchange to approximate an integral slippage
    return price    

def predict_b_to_get(price_b_over_a, ex_amount_a, ex_txn_fee=0.003):
    # predict the amount of b to get by exchanging ex_amount_a of a
  return price_b_over_a*(1-0.003)*ex_amount_a


def get_optimal_ex_amount_a(tolerance=100.):
    """
    exchange1: token a -> token b
    exchange2: token b -> token a

    return: optimal delta_x on exchange1 to make price difference vanished
    """
    # before flashloan
    print('############# Before Flashloan #############')
    uniswap_aux_over_wbtc, sushiswap_aux_over_wbtc = get_prices()

    # get reserves
    uniswap_aux_reserve, uniswap_wbtc_reserve, sushiswap_aux_reserve, sushiswap_wbtc_reserve = get_reserves(verbose=False)

    # determine trading direction
    if uniswap_aux_over_wbtc > sushiswap_aux_over_wbtc:
        reserv_a_ex1 = uniswap_wbtc_reserve  # on uni, wbtc is more expensive if uniswap_aux_over_wbtc is higher than sushiswap_aux_over_wbtc
        reserv_b_ex1 = uniswap_aux_reserve

        reserv_a_ex2 = sushiswap_wbtc_reserve
        reserv_b_ex2 = sushiswap_aux_reserve
        ex_direction = 'wbtc_to_aux_on_uni'
    else:
        reserv_a_ex1 = sushiswap_wbtc_reserve
        reserv_b_ex1 = sushiswap_aux_reserve

        reserv_a_ex2 = uniswap_wbtc_reserve
        reserv_b_ex2 = uniswap_aux_reserve
        ex_direction = 'wbtc_to_aux_on_sushi'

    ex_amount_a = None # amount of a to exchange on exchange1

    def predict_ex(ex_amount_a):
        pred_b_price_ex1 = predict_slippage(reserv_a_ex1, reserv_b_ex1, ex_amount_a, EXCHANGE_FEE)
        pred_b_get_from_ex1 = predict_b_to_get(pred_b_price_ex1, ex_amount_a, EXCHANGE_FEE)
        pred_a_price_ex2 = predict_slippage(reserv_b_ex2, reserv_a_ex2, pred_b_get_from_ex1, EXCHANGE_FEE)
        pred_a_get_from_ex2 = predict_b_to_get(pred_a_price_ex2, pred_b_get_from_ex1, EXCHANGE_FEE)

        profit_in_a = pred_a_get_from_ex2 - ex_amount_a
        sushiswap_aux_over_wbtc = (reserv_b_ex1 - pred_b_get_from_ex1) / (reserv_a_ex1 + ex_amount_a)
        uniswap_aux_over_wbtc = (reserv_b_ex2 + pred_b_get_from_ex1) / (reserv_a_ex2 - pred_a_get_from_ex2)

        return sushiswap_aux_over_wbtc, uniswap_aux_over_wbtc, profit_in_a

    grid_search_values = np.arange(0.01, 10, 0.01)  # the finer the grid search, the more accurate for the balanced condition
    for v in grid_search_values:
        sushiswap_aux_over_wbtc, uniswap_aux_over_wbtc, profit_in_a = predict_ex(v)
    
        # balanced condition
        # if sushiswap_aux_over_wbtc == uniswap_aux_over_wbtc:
        optimal_gap = np.abs(sushiswap_aux_over_wbtc - uniswap_aux_over_wbtc)
        # print(v, optimal_gap)
        if optimal_gap < tolerance:
            ex_amount_a = v
            break

    print('############# After Flashloan #############')
    print("Balance condition error tolerance: ", tolerance)
    print(f"After flashloan " + AUX_TOKEN + f"/wBTC exchange rate for Uniswap pool: {uniswap_aux_over_wbtc}")
    print(f"After flashloan " + AUX_TOKEN + f"/wBTC exchange rate for SushiSwap pool: {sushiswap_aux_over_wbtc}")
    print(f"Optimal amount of token a to exchange on Uniswap: {ex_amount_a}")
    print("Predicted profit of token a: ", profit_in_a)

    return ex_direction, ex_amount_a, profit_in_a

if __name__ == "__main__":

    # test
    uniswap_aux_reserve, uniswap_wbtc_reserve, sushiswap_aux_reserve, sushiswap_wbtc_reserve = get_reserves()
    uniswap_rate, sushiswap_rate = get_prices()

    ex_amount = 0.1
    sushiswap_aux_over_wbtc = predict_slippage(sushiswap_wbtc_reserve, sushiswap_aux_reserve, ex_amount, EXCHANGE_FEE)
    print(sushiswap_aux_over_wbtc)

    get_b_ex1 = predict_b_to_get(sushiswap_aux_over_wbtc, ex_amount, EXCHANGE_FEE)
    print(get_b_ex1)


    ex_direction, ex_amount_a, profit_in_a = get_optimal_ex_amount_a()
