# supported chains on debridge, but without Solana and Neon (don't change)
supported_chains = {
    "Ethereum": {
        "chainId": 1,
        "chainName": "Ethereum",
        "currency": "ETH",
        "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "rpc": [
            "https://ethereum-rpc.publicnode.com",
            "https://eth.llamarpc.com",
            "https://eth.drpc.org",
        ],
    },
    "Optimism": {
        "chainId": 10,
        "chainName": "Optimism",
        "currency": "ETH",
        "USDT": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
        "USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
        "rpc": [
            "https://optimism-rpc.publicnode.com",
            "https://optimism.llamarpc.com",
            "https://optimism.drpc.org",
        ],
    },
    "BSC": {
        "chainId": 56,
        "chainName": "BSC",
        "currency": "BNB",
        "USDT": "0x55d398326f99059ff775485246999027b3197955",
        "USDC": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
        "rpc": [
            "https://bsc-rpc.publicnode.com",
            "https://binance.llamarpc.com",
            "https://bsc.drpc.org",
        ],
    },
    "Polygon": {
        "chainId": 137,
        "chainName": "Polygon",
        "currency": "MATIC",
        "USDT": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
        "USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        "rpc": [
            "https://polygon-bor-rpc.publicnode.com",
            "https://polygon.llamarpc.com",
            "https://polygon-rpc.com",
        ],
    },
    "Base": {
        "chainId": 8453,
        "chainName": "Base",
        "currency": "ETH",
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "rpc": [
            "https://base-rpc.publicnode.com",
            "https://base.llamarpc.com",
            "https://base-mainnet.public.blastapi.io",
        ],
    },
    "Arbitrum": {
        "chainId": 42161,
        "chainName": "Arbitrum",
        "currency": "ETH",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "rpc": [
            "https://arbitrum-one.publicnode.com",
            "https://arbitrum.llamarpc.com",
            "https://arbitrum.drpc.org",
        ],
    },
    "Avalanche": {
        "chainId": 43114,
        "chainName": "Avalanche",
        "currency": "AVAX",
        "USDT": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
        "USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        "rpc": [
            "https://avalanche.public-rpc.com",
            "https://avax.meowrpc.com",
            "https://rpc.ankr.com/avalanche",
        ],
    },
    "Linea": {
        "chainId": 59144,
        "chainName": "Linea",
        "currency": "ETH",
        "USDC": "0x176211869cA2b568f2A7D4EE941E073a821EE1ff",
        "rpc": [
            "https://linea.decubate.com",
            "https://linea.drpc.org",
            "https://rpc.linea.build",
        ],
    },
}

# API url (don't change)
deBridge_api = "https://api.dln.trade/v1.0"

# start source chain from supported chains
src_chain = "Avalanche"

# start source token (native, USDT, USDC)
src_token = "native"

# min and max amount of currency to bridge at once
# they should be plus or minus the same
amount_range = {
    "ETH": [0.00033, 0.00066],
    "BNB": [0.018, 0.036],
    "MATIC": [14, 28],
    "AVAX": [0.30, 0.60],
    "USDT": [10, 20],
    "USDC": [10, 20],
}

# sleep range between transactions in seconds (in this example 60 - 120 seconds)
sleep_range = [5, 10]

# max gas price for each chain
max_gas_price = {
    "Ethereum": 60,
    "Optimism": 0.08,
    "BSC": 5,
    "Polygon": 210,
    "Base": 0.044,
    "Arbitrum": 0.17,
    "Avalanche": 30,
    "Linea": 0.15,
}

# max number of wallets for concurrent processing
# it's not recommended to use more than 10
max_wallets_concurrent = 10

# gas multiplier
GAS_ESTIMATION_MULTIPLIER = 1.05
GAS_PRICE_MULTIPLIER = 1.05

# ABI (don't change)
abi = """
[
    {
        "constant": true,
        "inputs": [
            {
                "name": "who",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
        {
            "name": "_spender",
            "type": "address"
        },
        {
            "name": "_value",
            "type": "uint256"
        }
        ],
        "name": "approve",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
"""
