import logging
from typing import Optional, Dict, Any
from sermon_publisher.plugins.podbean.client import PodbeanClient
from sermon_publisher.plugins.podbean.authenticate import PodbeanAuthenticator
from sermon_publisher.plugins.youtube.api import YouTubeAPI
from sermon_publisher.plugins.advanced_sermons_wp.sermon import Sermon
from sermon_publisher.exceptions.custom_exceptions import PluginInitializationError

class PluginFactory:
    """
    Factory for creating plugin instances based on configuration.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_podbean_authenticator(self) -> Optional[PodbeanAuthenticator]:
        if self.config.get('podbean'):
            try:
                self.logger.debug("Initializing PodbeanAuthenticator.")
                key = self.config.get('podbean_api_key')
                secret = self.config.get('podbean_api_secret')
                url = self.config.get('base_url')
                token_dir = self.config.get('token_directory', self.config.get('unpublished_audio_path'))  # Specify a separate directory if needed
                return PodbeanAuthenticator(key, secret, url, token_dir)
            except Exception as e:
                self.logger.error(f"Failed to initialize PodbeanAuthenticator: {e}")
                raise PluginInitializationError("PodbeanAuthenticator initialization failed.") from e
        self.logger.debug("PodbeanAuthenticator not enabled.")
        return None

    def create_podbean_client(self) -> Optional[PodbeanClient]:
        if self.config.get('podbean'):
            try:
                self.logger.debug("Initializing PodbeanClient.")
                authenticator = self.create_podbean_authenticator()
                if not authenticator:
                    self.logger.error("PodbeanAuthenticator is required for PodbeanClient.")
                    raise PluginInitializationError("PodbeanAuthenticator is required for PodbeanClient.")
                return PodbeanClient(authenticator, self.config)
            except Exception as e:
                self.logger.error(f"Failed to initialize PodbeanClient: {e}")
                raise PluginInitializationError("PodbeanClient initialization failed.") from e
        self.logger.debug("PodbeanClient not enabled.")
        return None

    def create_youtube_api(self) -> Optional[YouTubeAPI]:
        if self.config.get('youtube'):
            try:
                self.logger.debug("Initializing YouTubeAPI.")
                return YouTubeAPI(self.config)
            except Exception as e:
                self.logger.error(f"Failed to initialize YouTubeAPI: {e}")
                raise PluginInitializationError("YouTubeAPI initialization failed.") from e
        self.logger.debug("YouTubeAPI not enabled.")
        return None

    def create_sermon(self) -> Optional[Sermon]:
        if self.config.get('advanced_sermons'):
            try:
                self.logger.debug("Initializing Sermon.")
                return Sermon(self.config)
            except Exception as e:
                self.logger.error(f"Failed to initialize Sermon: {e}")
                raise PluginInitializationError("Sermon initialization failed.") from e
        self.logger.debug("Sermon not enabled.")
        return None
