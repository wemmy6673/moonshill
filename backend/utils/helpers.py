import redis
from functools import lru_cache
from config.settings import get_settings
from services.logging import init_logger
from web3 import Web3
from eth_account.messages import encode_defunct
from typing import Tuple


settings = get_settings()
logger = init_logger()


def verify_ethereum_signature(message: str, signature: str, address: str) -> Tuple[bool, str]:
    """
    Verify an Ethereum signature.

    Args:
        message (str): The original message that was signed
        signature (str): The signature to verify
        address (str): The Ethereum address that supposedly signed the message

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Create a Web3 instance
        w3 = Web3()

        # Encode the message
        message_encoded = encode_defunct(text=message)

        # Recover the address from the signature
        recovered_address = w3.eth.account.recover_message(message_encoded, signature=signature)

        # Compare the recovered address with the provided address (case-insensitive)
        is_valid = recovered_address.lower() == address.lower()

        logger.info(f"Recovered address: {recovered_address}, provided address: {address}")

        if not is_valid:
            return False, f"Signature verification failed. Recovered address {recovered_address} does not match {address}"

        return True, None

    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False, f"Error verifying signature: {str(e)}"


@lru_cache
def get_redis_instance(db: int = 0) -> redis.Redis:
    pool = redis.ConnectionPool.from_url(
        settings.redis_url,
        db=db,
        decode_responses=True,
        max_connections=10,
        socket_timeout=10,
        socket_connect_timeout=2,
        retry_on_timeout=True,
        socket_keepalive=True,
        health_check_interval=30
    )
    client = redis.Redis(connection_pool=pool)
    try:
        client.ping()
        logger.info(f"Redis connection successful (DB: {db}).")
    except redis.ConnectionError:
        logger.error(f"Failed to connect to Redis (DB: {db}): {e}")
        raise RuntimeError("Unable to connect to Redis")

    return client
