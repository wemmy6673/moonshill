from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
import tweepy
from services.logging import init_logger
from config.settings import get_settings
from utils.helpers import FetchUtil, FetchError
import asyncio

logger = init_logger()


class MarketData(BaseModel):
    price: float
    volume_24h: float
    market_cap: float
    price_change_24h: float
    last_updated: datetime


class TrendingTopic(BaseModel):
    name: str
    volume: int
    sentiment: float
    source: str
    url: str
    created_at: datetime


class AggregatedData(BaseModel):
    market_data: Optional[MarketData]
    trending_topics: List[TrendingTopic]
    relevant_news: List[Dict]
    token_movements: List[Dict]
    timestamp: datetime


class MarketDataService:
    """Service for fetching and aggregating market data from various sources."""

    def __init__(self):
        self.settings = get_settings()
        self.twitter_client = None
        self.coingecko_client = None
        self.dextools_client = None
        self.cryptocompare_client = None

    async def __aenter__(self):
        # Initialize API clients
        self.coingecko_client = FetchUtil.create_api_client(
            "https://api.coingecko.com/api/v3"
        )

        if self.settings.dextools_api_key:
            logger.info(f"Initializing DEXTools client")
            self.dextools_client = FetchUtil.create_api_client(
                "https://api.dextools.io/v1",
                api_key=self.settings.dextools_api_key
            )
        else:
            logger.warning("DEXTools API key not found, skipping initialization")

        if self.settings.cryptocompare_api_key:
            logger.info(f"Initializing CryptoCompare client")
            self.cryptocompare_client = FetchUtil.create_api_client(
                "https://min-api.cryptocompare.com/data/v2",
                api_key=self.settings.cryptocompare_api_key
            )
        else:
            logger.warning("CryptoCompare API key not found, skipping initialization")

        # Initialize Twitter client if credentials exist
        if all([
            hasattr(self.settings, 'twitter_client_id'),
            hasattr(self.settings, 'twitter_client_secret'),
            hasattr(self.settings, 'twitter_bearer_token')
        ]):
            logger.info(f"Initializing Twitter Market Data client")
            self.twitter_client = tweepy.Client(
                bearer_token=self.settings.twitter_bearer_token,
                consumer_key=self.settings.twitter_client_id,
                consumer_secret=self.settings.twitter_client_secret
            )
        else:
            logger.warning("Twitter Market Data client credentials not found, skipping initialization")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Clean up clients
        for client in [self.coingecko_client, self.dextools_client, self.cryptocompare_client]:
            if client:
                await client.__aexit__(exc_type, exc_val, exc_tb)

    async def fetch_market_data(self, token_address: str, blockchain: str = 'ethereum') -> Optional[MarketData]:
        """
        Fetch market data from CoinGecko API.

        Args:
            token_address: The token address to fetch data for
            blockchain: The blockchain name (e.g., 'ethereum', 'bsc', 'polygon')

        Returns:
            Optional[MarketData]: Market data if successful, None otherwise
        """
        try:
            async with self.coingecko_client as client:
                data = await client.get(
                    f"simple/token_price/{blockchain}",
                    params={
                        "contract_addresses": token_address,
                        "vs_currencies": "usd",
                        "include_24hr_vol": "true",
                        "include_24hr_change": "true",
                        "include_market_cap": "true",
                        "include_last_updated_at": "true"
                    }
                )

                if token_address.lower() in data:
                    token_data = data[token_address.lower()]
                    return MarketData(
                        price=token_data.get("usd", 0),
                        volume_24h=token_data.get("usd_24h_vol", 0),
                        market_cap=token_data.get("usd_market_cap", 0),
                        price_change_24h=token_data.get("usd_24h_change", 0),
                        last_updated=datetime.fromtimestamp(token_data.get("last_updated_at", 0))
                    )
        except FetchError as e:
            logger.error(f"Error fetching market data for {blockchain} token {token_address}: {str(e)}")
        return None

    async def fetch_trending_topics(self, keywords: Optional[List[str]] = None) -> List[TrendingTopic]:
        """Fetch trending topics from Twitter and other sources."""
        trending_topics = []

        if self.twitter_client:
            try:
                trends = self.twitter_client.get_place_trends(1)  # 1 is the WOEID for worldwide
                for trend in trends[0]["trends"]:
                    if not keywords or any(kw.lower() in trend["name"].lower() for kw in keywords):
                        trending_topics.append(TrendingTopic(
                            name=trend["name"],
                            volume=trend["tweet_volume"] or 0,
                            sentiment=0.0,  # Would need sentiment analysis service
                            source="twitter",
                            url=trend["url"],
                            created_at=datetime.now()
                        ))
            except Exception as e:
                logger.error(f"Error fetching Twitter trends: {str(e)}")

        return trending_topics

    async def fetch_token_movements(self, token_address: str) -> List[Dict]:
        """Fetch token movements from DEXTools API."""
        if not self.dextools_client:
            return []

        try:
            async with self.dextools_client as client:
                data = await client.get(f"token/{token_address}/trades")
                return data.get("data", [])[:10]  # Return last 10 trades
        except FetchError as e:
            logger.error(f"Error fetching token movements: {str(e)}")
        return []

    async def fetch_crypto_news(self, keywords: Optional[List[str]] = None) -> List[Dict]:
        """Fetch crypto news from various sources."""
        if not self.cryptocompare_client:
            return []

        news_items = []
        try:
            async with self.cryptocompare_client as client:
                data = await client.get("news/")
                for news in data.get("Data", []):
                    if not keywords or any(kw.lower() in news["title"].lower() for kw in keywords):
                        news_items.append({
                            "title": news["title"],
                            "url": news["url"],
                            "source": news["source"],
                            "published_at": datetime.fromtimestamp(news["published_on"]),
                            "categories": news.get("categories", "").split("|")
                        })
        except FetchError as e:
            logger.error(f"Error fetching crypto news: {str(e)}")

        return news_items

    async def get_campaign_market_data_context(
        self,
        token_address: Optional[str] = None,
        blockchain: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> AggregatedData:
        """
        Fetch and aggregate real-time data from multiple sources for campaign awareness.

        Args:
            token_address: Optional token address to fetch market data for
            blockchain: Optional blockchain name (e.g., 'ethereum', 'bsc', 'polygon')
            keywords: Optional list of keywords to filter data

        Returns:
            AggregatedData containing market data, trending topics, news, and token movements
        """
        # Initialize tasks list with non-token dependent fetches
        tasks = [
            self.fetch_trending_topics(keywords),
            self.fetch_crypto_news(keywords)
        ]

        # Add token-dependent fetches if token_address is provided
        if token_address:
            # Use provided blockchain or default to ethereum
            chain = blockchain.lower() if blockchain else 'ethereum'
            tasks.extend([
                self.fetch_market_data(token_address, chain),
                self.fetch_token_movements(token_address)
            ])

        # Fetch all data concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results based on whether token_address was provided
        if token_address:
            market_data, trending_topics, news, movements = results
        else:
            trending_topics, news = results
            market_data = None
            movements = []

        # Handle any exceptions in the results
        if isinstance(trending_topics, Exception):
            logger.error(f"Error fetching trending topics: {str(trending_topics)}")
            trending_topics = []
        if isinstance(news, Exception):
            logger.error(f"Error fetching news: {str(news)}")
            news = []
        if token_address:
            if isinstance(market_data, Exception):
                logger.error(f"Error fetching market data: {str(market_data)}")
                market_data = None
            if isinstance(movements, Exception):
                logger.error(f"Error fetching token movements: {str(movements)}")
                movements = []

        return AggregatedData(
            market_data=market_data,
            trending_topics=trending_topics,
            relevant_news=news,
            token_movements=movements,
            timestamp=datetime.now()
        )
