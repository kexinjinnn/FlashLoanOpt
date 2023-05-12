# Automated Flash Loan Arbitrage with Optimal Profit

This repository contains the code for the final report of course COS/ECE 473 at Princeton University. We propose an automatic bot that finds arbitrage opportunities, computes the optimal trading
amount, and executes flash loan transactions. The bot checks prices discrepancies, gas fees, transac-
tion fees, and slippage so that earnings are guaranteed. The bot supports arbitrary tokens on Uniswap
V2 and Sushiswap. We include some example tokens in the code. By default, we monitor the price of wBTC and LUSD. To add customized tokens, please go to common.py. To run this bot:

```
$ cd python_modules
$ python optimal_flashloan.py
```


