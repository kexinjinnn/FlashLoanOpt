
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

contract FlashLoanArbitrage {

    uint256 constant MAX_UINT = 2**256 - 1;

    // Address of the wBTC token contract
    address constant WBTC_TOKEN = 0x45AC379F019E48ca5dAC02E54F406F99F5088099;

    // Address of the LUSD token contract
    address constant LUSD_TOKEN = 0x4966Bb6Cd9f3e042331b0798525b7970eFB0D94A;

    // LETH address
    address constant LETH_TOKEN = 0xb85154E1948e52214A5F134172358Fb5010F6282;

    // WETH address
    address constant WETH_TOKEN = 0xCCB14936C2E000ED8393A571D15A2672537838Ad;

    // Addresses of the SushiSwap and Uniswap V2 routers we will be interacting with to perform the swaps
    address constant SUSHISWAP_ROUTER = 0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506;
    address constant UNISWAP_ROUTER = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;

    // Address of the Aave pool we will be flash loaning from
    address constant AAVE_POOL = 0x7b5C526B7F8dfdff278b4a3e045083FBA4028790;

    address[] private addresses;
    uint256 private amounts;
    uint8[] private swap_path;

    constructor() {

    }

    /**
     * @dev The entry point to this contract to perform the arbitrage. 
            we flash loan amount of asset1 from the Aave pool and always perform swap it
            for asset2 using the dex1, and then swap the asset2 back to asset1 using the
            dex2.
     */
    function arbitrage(address asset1, address asset2, uint256 amount, uint8 dex1, uint8 dex2) external {
        // save global vars
        addresses = [asset1, asset2];
        amounts = amount;
        swap_path = [dex1, dex2];

        // Call the flash loan function in the Aave pool contract
        IERC20(asset1).approve(AAVE_POOL, MAX_UINT);
        IPool(AAVE_POOL).flashLoanSimple(
            address(this), // receiverAddress: this contract
            asset1,
            amount,
            "", // params: not relevant here
            0 // referralCode: not relevant here
        );

        // Any amount of asset1 in the contract is our profit
        IERC20 token = IERC20(asset1);
        uint256 profit = IERC20(asset1).balanceOf(address(this));

        // Send profit to caller
        token.transfer(msg.sender, profit);
    }

    function get_path(address tokenIn, address tokenOut) internal pure returns (address[] memory) {
      address[] memory path = new address[](2);
      path[0] = tokenIn;
      path[1] = tokenOut;
      return path;
    }


    /**
     * @dev The callback function that will be invoked by the Aave contract.
     * @param asset The address of the flash-borrowed asset
     * @param amount The amount of the flash-borrowed asset
     * @param premium The fee of the flash-borrowed asset
     * @param initiator The address of the flashloan initiator
     * @param params The byte-encoded params passed when initiating the flashloan
     * @return True if the execution of the operation succeeds, false otherwise
     */
    function executeOperation(
        address asset,
        uint256 amount,
        uint256 premium,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
       
        IUniswapV2Router02 sushiswapRouter = IUniswapV2Router02(SUSHISWAP_ROUTER);
        IUniswapV2Router02 uniswapRouter = IUniswapV2Router02(UNISWAP_ROUTER);


        /***** Swap asset1 for asset2 at dex1 then swap it back at dex2 *****/


        // 0, 1 means swap on sushi then uni
        if (swap_path[0] == 0 && swap_path[1] == 1){
            IERC20(addresses[0]).approve(SUSHISWAP_ROUTER, MAX_UINT);
            sushiswapRouter.swapExactTokensForTokens(
                amount, // amountIn: amount of asset1
                0, // amountOutMin: minimum acceptable asset2 received
                get_path(addresses[0], addresses[1]), // path: swap path
                address(this), // to: this contract
                block.timestamp // deadline: latest acceptable time to complete the swap by
            );
            IERC20(addresses[1]).approve(UNISWAP_ROUTER, MAX_UINT);
            uniswapRouter.swapExactTokensForTokens(
                IERC20(addresses[1]).balanceOf(address(this)), // amountIn: amount of aseet2
                0, // amountOutMin: minimum acceptable asset1 received
                get_path(addresses[1], addresses[0]), // path: swap path
                address(this), // to: this contract
                block.timestamp // deadline: latest acceptable time to complete the swap by
            );

        }
        // 1, 0 means swap on uni then sushi
        if (swap_path[0] == 1 && swap_path[1] == 0){
            IERC20(addresses[0]).approve(UNISWAP_ROUTER, MAX_UINT);
            uniswapRouter.swapExactTokensForTokens(
                amount, // amountIn: amount of asset1
                0, // amountOutMin: minimum acceptable asset2 received
                get_path(addresses[0], addresses[1]), // path: swap path
                address(this), // to: this contract
                block.timestamp // deadline: latest acceptable time to complete the swap by
            );
            IERC20(addresses[1]).approve(SUSHISWAP_ROUTER, MAX_UINT);
            sushiswapRouter.swapExactTokensForTokens(
                IERC20(addresses[1]).balanceOf(address(this)), // amountIn: amount of asset2
                0, // amountOutMin: minimum acceptable asset1 received
                get_path(addresses[1], addresses[0]), // path: swap path
                address(this), // to: this contract
                block.timestamp // deadline: latest acceptable time to complete the swap by
            );
        }

        return true;
    }
}

/**
 * @dev Partial interface for a Uniswap V2 router contract (SushiSwap pools use the same interface).
 */
interface IUniswapV2Router02 {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}

/**
 * @dev Partial interface for an Aave V3 pool contract.
 */
interface IPool {
    function flashLoanSimple(
        address receiverAddress,
        address asset,
        uint256 amount,
        bytes calldata params,
        uint16 referralCode
    ) external;
}

/**
 * @dev Partial interface for an ERC-20 token.
 */
interface IERC20 {
    function balanceOf(address account) external view returns (uint256);

    function transfer(address to, uint256 amount) external returns (bool);

    function approve(address spender, uint256 amount) external returns (bool);
}