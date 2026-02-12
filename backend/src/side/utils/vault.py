import keyring
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SecretVault:
    """
    Secure wrapper for OS-native credential storage (Keychain, Secret Service, etc.)
    Provides Palantir-level isolation for sensitive Sidelith tokens.
    """
    SERVICE_NAME = "sidelith-cli"
    
    @classmethod
    def store_token(cls, project_id: str, token: str) -> bool:
        """Stores the access token for a specific project securely."""
        try:
            keyring.set_password(cls.SERVICE_NAME, project_id, token)
            return True
        except Exception as e:
            logger.error(f"Vault Error: Failed to store token in OS keychain: {e}")
            return False

    @classmethod
    def get_token(cls, project_id: str) -> Optional[str]:
        """Retrieves the access token from the secure vault."""
        try:
            return keyring.get_password(cls.SERVICE_NAME, project_id)
        except Exception as e:
            logger.error(f"Vault Error: Failed to retrieve token from OS keychain: {e}")
            return None

    @classmethod
    def delete_token(cls, project_id: str) -> bool:
        """Removes the token from the vault."""
        try:
            keyring.delete_password(cls.SERVICE_NAME, project_id)
            return True
        except Exception as e:
            logger.debug(f"Vault Info: No token found to delete for {project_id}: {e}")
            return False
