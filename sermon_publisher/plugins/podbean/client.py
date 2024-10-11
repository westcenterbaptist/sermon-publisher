import logging
from typing import Dict, Any, Optional

from sermon_publisher.plugins.podbean.authenticate import PodbeanAuthenticator
from sermon_publisher.plugins.podbean.episode import EpisodeProcessor
from sermon_publisher.exceptions.custom_exceptions import PodbeanClientError

class PodbeanClient:
    """
    Handles general interactions with the Podbean API.
    """

    def __init__(self, authenticator: PodbeanAuthenticator, config: Dict[str, Any]):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.authenticator = authenticator
        self.config = config
        self.urls = {
            'auth_upload': 'https://api.podbean.com/v1/upload',
            'episodes': 'https://api.podbean.com/v1/episodes',
            'podcast_id': 'https://api.podbean.com/v1/podcast',
            # Add other necessary endpoints
        }

    def get_episode_processor(self) -> EpisodeProcessor:
        """
        Returns an instance of EpisodeProcessor.

        :return: EpisodeProcessor instance.
        """
        try:
            self.logger.debug("Initializing EpisodeProcessor.")
            return EpisodeProcessor(
                unpublished_audio_path=self.config.get('unpublished_audio_path'),
                published_audio_path=self.config.get('published_audio_path'),
                image_path=self.config.get('podbean_image_path'),
                content=self.config.get('episode_content'),
                publish=self.config.get('publish_audio'),
                urls=self.urls,
                authenticator=self.authenticator
            )
        except Exception as e:
            self.logger.error(f"Failed to create EpisodeProcessor: {e}")
            raise PodbeanClientError("Failed to create EpisodeProcessor.") from e