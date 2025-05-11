from config.settings import get_settings
from services.logging import init_logger
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.hashes import Hash, SHA256
from datetime import timedelta
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.exceptions import InvalidKey
from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer


logger = init_logger()
settings = get_settings()


access_security = JwtAccessBearer(
    secret_key=settings.jwt_secret,
    auto_error=False,
    access_expires_delta=timedelta(seconds=settings.jwt_expiry)
)


refresh_security = JwtRefreshBearer(
    secret_key=settings.jwt_secret,
    auto_error=True
)


def sha256(message: str) -> str:

    digest = Hash(SHA256())
    digest.update(message.encode())
    _bytes = digest.finalize()
    return b64encode(_bytes).decode()


def hash_password(password: str) -> str:
    """ Hashes a password with scrypt """

    try:

        kdf = Scrypt(salt=settings.password_salt.encode(),
                     n=2 ** 14, r=8, p=2, length=32)

        encoded_hash = b64encode((kdf.derive(password.encode()))).decode()

        return encoded_hash

    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        return None


def verify_password(password: str, password_hash: str) -> bool:
    """ Verifies a password with scrypt """

    try:

        kdf = Scrypt(salt=settings.password_salt.encode(),
                     n=2 ** 14, r=8, p=2, length=32)

        kdf.verify(password.encode(), b64decode(password_hash))

        return True

    except InvalidKey as e:

        return False

    except Exception as e:

        logger.error(f"Error verifying password: {str(e)}")
        return False
