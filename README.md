# debridge-burner

debridge-burner is an asynchronous script designed to run the balance on deBridge, which allows you to farm points by burning the wallet balance on the platform commission, thereby earning points. It allows you to burn the balance of several wallets at the same time (up to 10 or more at the user's request).

## Disclaimer

By using this script, you acknowledge that you do so at your own risk. I, as the creator of this script, do not assume any responsibility or liability for any financial losses or damages incurred as a result of using this script.

**No Guarantees:** While efforts have been made to ensure the accuracy and reliability of the script, there is no guarantee that it will function as intended under all circumstances. The script may have bugs, errors, or vulnerabilities that could result in unexpected behavior.

**By using this script, you agree to these terms and conditions.**

## Requirements

Python 3.11 or higher (not tested on previous versions)
Libraries: web3, colorama, colorlog, art

## Installation

Clone this script
```bash
git clone https://github.com/Dellenoam/debridge-burner.git
```

Create and active virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install requirement dependencies from requirements.txt
```bash
pip install -r requirements.txt
```

## Configuration

The script offers several customizable settings:

src_chain

`The starting source chain from the supported chains.`

src_token

`The starting source token (native, USDT, USDC).`

amount_range

`Minimum and maximum amounts of currency to bridge at once for different currencies.`

sleep_range

`Range of sleep time between transactions in seconds.`

max_gas_price

`Maximum gas price for each supported chain.`

max_wallets_concurrent

`Maximum number of wallets for concurrent processing (not recommended to use more than 10).`

GAS_ESTIMATION_MULTIPLIER

`Gas estimation multiplier.`

GAS_PRICE_MULTIPLIER

`Gas price multiplier.`

## Usage

Configure settings in config.py and then you can run it using command below

```bash
python main.py
```
