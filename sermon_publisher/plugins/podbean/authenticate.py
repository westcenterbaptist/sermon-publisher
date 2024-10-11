import os
import json
import base64
import logging
import requests
from datetime import datetime, timedelta
from sermon_publisher.exceptions.custom_exceptions import PodbeanAuthError

class PodbeanAuthenticator:
    """
    Handles authentication with the Podbean API.
    """

    def __init__(self, key: str, secret: str, podbean_api_url: str, token_dir: str = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.key = key
        self.secret = secret
        self.podbean_api_url = podbean_api_url.rstrip('/')  # Ensure no trailing slash
        if token_dir is None:
            # Default to project root
            self.token_path = os.path.join(os.getcwd(), 'token.json')
        else:
            self.token_path = os.path.join(token_dir, 'token.json')
        self.access_token = None
        self.authenticate()

    def authenticate(self) -> None:
        """
        Authenticates with Podbean API and retrieves an access token.
        """
        if self.validate_token():
            self.logger.debug("Existing token is valid.")
            self.access_token = self.get_token()['access_token']
            return

        self.logger.debug("Existing token is invalid or not found. Initiating authentication.")
        credentials = f"{self.key}:{self.secret}".encode()
        encoded_credentials = base64.b64encode(credentials).decode()

        headers = {'Authorization': f'Basic {encoded_credentials}'}
        data = {'grant_type': 'client_credentials'}

        oauth_token_url = f"{self.podbean_api_url}/oauth/token"
        self.logger.debug(f"OAuth Token URL: {oauth_token_url}")

        try:
            response = requests.post(oauth_token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data['expires_in']
            self.save_token(self.access_token, expires_in)
            self.logger.info("Authentication successful. Access token obtained.")
        except requests.RequestException as e:
            self.logger.error(f"Failed to authenticate with Podbean API: {e}")
            raise PodbeanAuthError("Authentication with Podbean API failed.") from e

    def validate_token(self) -> bool:
        """
        Validates if the existing token is still valid.

        :return: True if valid, False otherwise.
        """
        if not os.path.exists(self.token_path):
            self.logger.debug("Token file does not exist.")
            return False

        try:
            token_data = self.get_token()
            expiration_time = datetime.fromisoformat(token_data['expiration_time'])
            is_valid = datetime.now() <= expiration_time
            self.logger.debug(f"Token valid: {is_valid}")
            return is_valid
        except (IOError, ValueError, KeyError) as e:
            self.logger.warning(f"Failed to validate token: {e}")
            return False

    def save_token(self, access_token: str, expires_in: int) -> None:
        """
        Saves the access token and its expiration time to a file.

        :param access_token: The access token string.
        :param expires_in: Token validity duration in seconds.
        """
        expiration_time = datetime.now() + timedelta(seconds=expires_in)
        token_data = {
            'access_token': access_token,
            'expiration_time': expiration_time.isoformat()
        }

        try:
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f)
            self.logger.debug(f"Token saved to {self.token_path}.")
        except IOError as e:
            self.logger.error(f"Failed to save token: {e}")
            raise PodbeanAuthError("Failed to save access token.") from e

    def get_token(self) -> dict:
        """
        Retrieves the token data from the token file.

        :return: Dictionary containing token data.
        """
        try:
            with open(self.token_path, 'r') as f:
                token_data = json.load(f)
            self.logger.debug("Token data retrieved successfully.")
            return token_data
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to read token file: {e}")
            raise PodbeanAuthError("Failed to read access token.") from e

    def remove_token(self) -> None:
        """
        Removes the token file.
        """
        try:
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
                self.logger.info("Token file removed successfully.")
        except OSError as e:
            self.logger.error(f"Failed to remove token file: {e}")
            raise PodbeanAuthError("Failed to remove access token.") from e
