from pydantic import BaseModel, Field, field_validator, ValidationError, EmailStr
from pydantic_settings import SettingsConfigDict
from datetime import datetime
from eth_utils import is_address
from typing import Optional, Dict, Any


class AccessToken(BaseModel):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(alias="tokenType")

    model_config = SettingsConfigDict(populate_by_name=True)


class AccessTokenRequest(BaseModel):
    message: str = Field(min_length=1)
    signature: str = Field(min_length=32)
    owner_address: str = Field(min_length=42, alias="ownerAddress")

    model_config = SettingsConfigDict(populate_by_name=True)


class CreateWorkspace(AccessTokenRequest):
    name: str = Field(min_length=3, max_length=128)
    notification_email: Optional[EmailStr] = Field(default=None, alias="notificationEmail")
    price_tag: Optional[str] = Field(default=None, alias="priceTag")

    model_config = SettingsConfigDict(populate_by_name=True)

    @field_validator("owner_address")
    @classmethod
    def validate_owner_address(cls, v:  str) -> str:
        is_valid = is_address(v)
        if not is_valid:
            raise ValidationError(f"Invalid Ethereum address: {v}", model=cls)
        return v


class Workspace(BaseModel):
    id: int
    name: str = Field(min_length=3, max_length=128)
    owner_address: str = Field(min_length=42, max_length=42, alias="ownerAddress")
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(populate_by_name=True)

    @field_validator("owner_address")
    @classmethod
    def validate_owner_address(cls, v: str) -> str:
        is_valid = is_address(v)
        if not is_valid:
            raise ValidationError(f"Invalid Ethereum address: {v}", model=cls)
        return v


class PriceTagValidationRequest(BaseModel):
    """Request model for price tag validation"""
    price_tag: str = Field(alias="priceTag")

    model_config = SettingsConfigDict(populate_by_name=True)


class PriceTagValidation(BaseModel):
    """Response model for price tag validation"""
    is_valid: bool = Field(alias="isValid")
    details: Optional[Dict[str, Any]] = None

    model_config = SettingsConfigDict(populate_by_name=True)
