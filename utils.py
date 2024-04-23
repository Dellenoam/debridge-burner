import logging
import os
from functools import lru_cache
import re

import colorlog

from config import supported_chains, amount_range

def get_contract_address(token: str, chain: str) -> str:
    if token in ["USDT", "USDC"]:
        token_address = supported_chains[chain].get(token)

        if not token_address:
            raise ValueError(
                f"There is no known contract address for {token} on {chain}"
            )
    else:
        token_address = "0x0000000000000000000000000000000000000000"

    return token_address


def get_available_tokens_for_chain(chain: str) -> list[str]:
    usdt_available = supported_chains[chain].get("USDT")
    usdc_available = supported_chains[chain].get("USDC")

    available_tokens_for_chain = ["native"]

    if usdt_available:
        available_tokens_for_chain.append("USDT")
    if usdc_available:
        available_tokens_for_chain.append("USDC")
    
    return available_tokens_for_chain


@lru_cache
def setup_logging(log_file) -> logging.Logger:
    if not os.path.exists(log_file):
        with open(log_file, "w"):
            pass

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    stream_handler = colorlog.StreamHandler()
    stream_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s:%(reset)s %(message)s',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        },
        secondary_log_colors={},
        style='%'
    ))
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    def highlight_entities(record):
        entities = ['address', 'currency', 'chain']
        patterns = {
            'address': r'0x[a-fA-F0-9]{40}',
            'currency': '|'.join(amount_range.keys()),
            'chain': '|'.join(supported_chains.keys())
        }
        colors = {
            'address': '\033[36m',
            'currency': '\033[33m',
            'chain': '\033[35m'
        }
        message = record.getMessage()
        for entity in entities:
            pattern = patterns[entity]
            color = colors[entity]
            message = re.sub(pattern, lambda x: f'{color}{x.group(0)}\033[0m', message)
        record.msg = message
        return True

    logger.addFilter(highlight_entities)

    return logger
