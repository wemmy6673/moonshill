from enum import StrEnum


class EmailTemplate(StrEnum):
    CAMPAIGN_PUBLISHED = "CAMPAIGN_PUBLISHED"


class CampaignStatus(StrEnum):
    PENDING = "PENDING"
    PAUSED = "PAUSED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CampaignTimeline(StrEnum):
    ONE_WEEK = "1 Week"
    TWO_WEEKS = "2 Weeks"
    ONE_MONTH = "1 Month"
    TWO_MONTHS = "2 Months"
    THREE_MONTHS = "3 Months"
    SIX_MONTHS = "6 Months"
    ONE_YEAR = "1 Year"


class CampaignType(StrEnum):
    MEME_SHILLING = "Meme Shilling"
    TOKEN_LAUNCH = "Token Launch"
    PRICE_ACTION = "Price Action"
    COMMUNITY_GROWTH = "Community Growth"
    PARTNERSHIP = "Partnership Shilling"
    CUSTOM = "Custom Shilling"


class TargetPlatform(StrEnum):
    TWITTER = "Twitter"
    TELEGRAM = "Telegram"
    DISCORD = "Discord"


class EngagementStyle(StrEnum):
    STANDARD = "Standard"
    AGGRESSIVE = "Aggressive"
    PASSIVE = "Passive"


class TargetAudience(StrEnum):
    ACTIVE_TRADERS = "Active Traders"
    LONG_TERM_INVESTORS = "Long-Term Investors"
    DEFI_ENTHUSIASTS = "DeFi Enthusiasts"
    CRYPTO_INFLUENCERS = "Crypto Influencers"


class CampaignGoal(StrEnum):
    BRAND_AWARENESS = "Brand Awareness"
    COMMUNITY_ENGAGEMENT = "Community Engagement"
    INCREASE_HOLDERS = "Increase Holders"
    TRADING_VOLUME = "Trading Volume"


class Blockchain(StrEnum):
    ethereum = "ETHEREUM"
