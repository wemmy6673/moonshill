import redis
from functools import lru_cache
from config.settings import get_settings
from services.logging import init_logger
from web3 import Web3
from eth_account.messages import encode_defunct
from typing import Tuple, Optional, Dict, Any
import httpx
import asyncio


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


class FetchError(Exception):
    """Custom exception for fetch errors"""
    pass


class FetchUtil:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=30.0,
                follow_redirects=True
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            self.client = None

    async def ensure_client(self):
        """Ensure client exists and is not closed"""
        async with self._lock:
            if not self.client:
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    headers=self.headers,
                    timeout=30.0,
                    follow_redirects=True
                )

    @lru_cache(maxsize=100)
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Make a GET request with caching and error handling

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds

        Returns:
            Dict containing the response data

        Raises:
            FetchError: If the request fails
        """
        await self.ensure_client()

        request_headers = {**self.headers, **(headers or {})}

        try:
            response = await self.client.get(
                endpoint.lstrip('/'),
                params=params,
                headers=request_headers,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise FetchError(f"Request timed out after {timeout} seconds")
        except httpx.HTTPStatusError as e:
            raise FetchError(f"Request failed with status {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise FetchError(f"Request failed: {str(e)}")
        except Exception as e:
            raise FetchError(f"Unexpected error: {str(e)}")

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Make a POST request with error handling

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            headers: Additional headers
            timeout: Request timeout in seconds

        Returns:
            Dict containing the response data

        Raises:
            FetchError: If the request fails
        """
        await self.ensure_client()

        request_headers = {**self.headers, **(headers or {})}

        try:
            response = await self.client.post(
                endpoint.lstrip('/'),
                data=data,
                json=json,
                headers=request_headers,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise FetchError(f"Request timed out after {timeout} seconds")
        except httpx.HTTPStatusError as e:
            raise FetchError(f"Request failed with status {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise FetchError(f"Request failed: {str(e)}")
        except Exception as e:
            raise FetchError(f"Unexpected error: {str(e)}")

    @staticmethod
    def create_api_client(
        base_url: str,
        api_key: Optional[str] = None,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> 'FetchUtil':
        """
        Create a new API client with proper headers

        Args:
            base_url: Base URL for the API
            api_key: Optional API key
            additional_headers: Additional headers to include

        Returns:
            Configured FetchUtil instance
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            **(additional_headers or {})
        }

        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        return FetchUtil(base_url, headers)
