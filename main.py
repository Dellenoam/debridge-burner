import asyncio
import random

from aiohttp import ClientResponseError
from eth_typing import ChecksumAddress

import config
import services
from utils import get_available_tokens_for_chain, get_contract_address, setup_logging

logger = setup_logging("debridge_burner.log")


async def process_wallet(
    manager: services.Web3Manager,
    address: ChecksumAddress,
    private_key: str,
    src_chain: str,
    src_token: str,
    dst_chain: str,
    dst_token: str,
    is_native: bool,
) -> None:
    """
    Process a wallet by sending transactions to the specified destination chain.
    """
    src_token_address = get_contract_address(src_token, src_chain)
    src_token_address = manager.web3.to_checksum_address(src_token_address)

    dst_token_address = get_contract_address(dst_token, dst_chain)
    dst_token_address = manager.web3.to_checksum_address(dst_token_address)

    amount_range = config.amount_range[src_token]
    amount = random.uniform(*amount_range)

    logger.info(
        f"Sending {amount} {src_token} from {src_chain} to {dst_token} on {dst_chain} with address {address}"
    )

    amount_in_decimals = (
        manager.web3.to_wei(amount, "ether")
        if is_native
        else round(amount * 10 ** (await manager.get_decimals(src_token_address)))
    )

    debridge_data = await services.create_debridge_tx(
        address,
        config.supported_chains[src_chain]["chainId"],
        config.supported_chains[dst_chain]["chainId"],
        src_token_address,
        dst_token_address,
        amount_in_decimals,
    )

    if debridge_data is None:
        logger.warning("Failed to create debridge transaction via API after 3 attempts")
        print()
        return

    debridge_tx_data = debridge_data["tx"]
    tx_amount = int(debridge_data["estimation"]["srcChainTokenIn"]["amount"])

    tx = await manager.create_tx(
        address,
        private_key,
        debridge_tx_data,
        src_token_address,
        src_chain,
        config.supported_chains[src_chain]["chainId"],
        is_native=is_native,
        tx_amount=tx_amount,
    )

    if not tx:
        logger.warning(
            f"Transaction {amount} {src_token} from {src_chain} to {dst_token} on {dst_chain} with address {address} failed"
        )
        print()

        return

    logger.info(
        f"Transaction {amount} {src_token} from {src_chain} to {dst_token} on {dst_chain} with address {address} sent"
    )
    print()


async def main() -> None:
    """
    Asynchronous function that creates and sends transactions for each wallet in the wallet_private_keys.txt file.
    """
    private_keys = [line.strip() for line in open("wallet_private_keys.txt", "r")]
    semaphore = asyncio.Semaphore(config.max_wallets_concurrent)

    async def pre_process_wallet(private_key: str) -> None:
        async with semaphore:
            src_chain = config.src_chain
            src_token = config.src_token

            src_token = (
                config.supported_chains[src_chain]["currency"]
                if src_token == "native"
                else src_token
            )

            balance_sufficient = False
            balance_sufficient_try = False

            while True:
                if src_token not in ["USDT", "USDC"]:
                    is_native = True
                else:
                    is_native = False

                dst_chain = random.choice(
                    [
                        chain
                        for chain in config.supported_chains.keys()
                        if chain != src_chain
                    ]
                )
                dst_token = random.choice(get_available_tokens_for_chain(dst_chain))

                if dst_token == "native":
                    dst_token = config.supported_chains[dst_chain]["currency"]

                for rpc in config.supported_chains[src_chain]["rpc"]:
                    try:
                        manager = services.Web3Manager(rpc)

                        account = manager.web3.eth.account.from_key(private_key)
                        address = manager.web3.to_checksum_address(account.address)

                        if (await manager.get_balance(address)) < config.amount_range[
                            src_token
                        ][1]:
                            if balance_sufficient_try:
                                break

                            logger.info(
                                f"Skipping {src_token} from {src_chain} to {dst_chain} with address {address} because balance is too low"
                            )
                            print()

                            balance_sufficient_try = True
                            break

                        balance_sufficient = True

                        await process_wallet(
                            manager,
                            address,
                            private_key,
                            src_chain,
                            src_token,
                            dst_chain,
                            dst_token,
                            is_native,
                        )

                        break
                    except ClientResponseError:
                        continue

                logger.info("Sleeping...")
                print()
                await asyncio.sleep(
                    random.uniform(config.sleep_range[0], config.sleep_range[1])
                )

                if not balance_sufficient:
                    src_chain, src_token = dst_chain, dst_token

                    if not balance_sufficient_try:
                        balance_sufficient_try = True
                        continue
                    else:
                        logger.info(f"Wallet {address} balance is not sufficient")
                        print()
                        break

    await asyncio.gather(
        *[pre_process_wallet(private_key) for private_key in private_keys]
    )


if __name__ == "__main__":
    from art import text2art
    import colorama

    art = colorama.Fore.MAGENTA + text2art("debridge-burner") + colorama.Style.RESET_ALL

    print(art)

    asyncio.run(main())
