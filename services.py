import asyncio
from decimal import Decimal
from typing import Any, Dict

import aiohttp
from eth_typing import ChecksumAddress
from web3 import AsyncHTTPProvider, AsyncWeb3
from web3.types import Wei

from config import (
    GAS_ESTIMATION_MULTIPLIER,
    GAS_PRICE_MULTIPLIER,
    abi,
    deBridge_api,
    max_gas_price,
)
from utils import setup_logging

logger = setup_logging("debridge_burner.log")


class Web3Manager:
    def __init__(self, rpc):
        self.web3 = AsyncWeb3(AsyncHTTPProvider(rpc))

    async def get_balance(
        self, address: ChecksumAddress, use_ether: bool = True
    ) -> int | Decimal | Wei:
        balance = await self.web3.eth.get_balance(address)

        if use_ether:
            balance = self.web3.from_wei(balance, "ether")

        return balance

    async def get_balance_from_contract(
        self, address: str, contract_address: ChecksumAddress, use_ether: bool = True
    ) -> int | Decimal | Wei:
        contract = self.web3.eth.contract(address=contract_address, abi=abi)

        balance = await contract.functions.balanceOf(address).call()

        if use_ether:
            decimals = await contract.functions.decimals().call()
            balance = balance / 10**decimals

        return balance

    async def get_decimals(self, contract_address: ChecksumAddress) -> int:
        contract = self.web3.eth.contract(address=contract_address, abi=abi)

        decimals = await contract.functions.decimals().call()

        return decimals

    async def create_tx(
        self,
        address: ChecksumAddress,
        private_key: str,
        data_for_tx: Dict[str, str | int],
        chain_token_address: ChecksumAddress,
        chain: str,
        chain_id: int,
        is_native: bool,
        tx_amount: int,
    ) -> bool:
        try:
            gas_price = self.web3.to_wei(
                await self.web3.eth.gas_price * GAS_PRICE_MULTIPLIER, "wei"
            )
            gas_price_in_gwei = self.web3.from_wei(gas_price, "gwei")

            logger.info(f"Gas price for this transaction: {gas_price_in_gwei} gwei")

            if gas_price_in_gwei > max_gas_price[chain]:
                logger.info("Gas price is too high")
                return False

            smart_contract_tx = {
                "to": data_for_tx["to"],
                "value": int(data_for_tx["value"]),
                "data": data_for_tx["data"],
                "chainId": chain_id,
                "gasPrice": gas_price,
                "gas": 0,
                "nonce": await self.web3.eth.get_transaction_count(address),
            }

            smart_contract_tx["gas"] = int(
                await self.web3.eth.estimate_gas(smart_contract_tx)
                * GAS_ESTIMATION_MULTIPLIER
            )

            if await self.get_balance(address) < smart_contract_tx["gas"] * gas_price:
                logger.info(f"Not enough funds for gas on {chain} address {address}")
                return False

            if not is_native:
                tx_approval = await self._approve_token_transaction(
                    address,
                    private_key,
                    chain,
                    chain_token_address,
                    data_for_tx["to"],
                    tx_amount,
                    gas_price,
                )

                if not tx_approval:
                    return False

            await self._send_transaction(
                smart_contract_tx, private_key, "Bridge transaction"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            return False

    async def _approve_token_transaction(
        self, address, private_key, chain, chain_token_address, to, tx_amount, gas_price
    ) -> bool:
        token_contract = self.web3.eth.contract(address=chain_token_address, abi=abi)
        approve_tx = await token_contract.functions.approve(
            to, tx_amount
        ).build_transaction(
            {
                "from": address,
                "nonce": await self.web3.eth.get_transaction_count(address),
                "gasPrice": gas_price,
                "gas": 0,
            }
        )

        approve_tx["gas"] = int(
            await self.web3.eth.estimate_gas(approve_tx) * GAS_ESTIMATION_MULTIPLIER
        )

        logger.info(f"Estimated gas for approval: {approve_tx['gas']}")

        if await self.get_balance(address) < approve_tx["gas"] * gas_price:
            logger.info(f"Not enough funds for gas on {chain} address {address}")

            return False

        await self._send_transaction(approve_tx, private_key, "Approval transaction")

        return True

    async def _send_transaction(self, tx, private_key, tx_type):
        signed_tx = await self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        logger.info(f"{tx_type} hash: {tx_hash.hex()}")

        tx_receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)

        logger.info(f"{tx_type} receipt: {tx_receipt}")


async def create_debridge_tx(
    address: ChecksumAddress,
    src_chain: int,
    dst_chain: int,
    src_chain_token_address: ChecksumAddress,
    dst_chain_token_address: ChecksumAddress,
    amount_in_decimals: float,
) -> Dict[str, Any] | None:
    response = None

    for attempt in range(3):
        async with aiohttp.ClientSession() as session:
            url = f"{deBridge_api}/dln/order/create-tx"
            params = {
                "srcChainId": src_chain,
                "srcChainTokenIn": src_chain_token_address,
                "srcChainTokenInAmount": amount_in_decimals,
                "dstChainId": dst_chain,
                "dstChainTokenOut": dst_chain_token_address,
                "dstChainTokenOutRecipient": address,
                "srcChainOrderAuthorityAddress": address,
                "dstChainOrderAuthorityAddress": address,
                "referralCode": "",
            }
            async with session.get(url, params=params) as response:
                response_status = response.status
                response = await response.json()
                if response_status == 200 and "errorCode" not in response:
                    return response
                else:
                    await asyncio.sleep(3**attempt)

    if response and "errorMessage" in response:
        logger.warning(f"deBridge API error message: {response['errorMessage']}")

    return None
