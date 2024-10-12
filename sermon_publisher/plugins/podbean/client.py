import logging
import requests
from typing import Dict, Any, Optional
from sermon_publisher.plugins.podbean.authenticate import PodbeanAuthenticator
from sermon_publisher.plugins.podbean.episode import EpisodeProcessor
from sermon_publisher.exceptions.custom_exceptions import PodbeanClientError, PodbeanEpisodeError

class PodbeanClient:
    """
    Handles general interactions with the Podbean API.
    """

    def __init__(self, authenticator: PodbeanAuthenticator, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.authenticator = authenticator
        self.urls = {
            'auth_upload': f"{self.config.get('podbean_api_url')}files/uploadAuthorize",
            'episodes': f"{self.config.get('podbean_api_url')}episodes",
            'podcast_id': f"{self.config.get('podbean_api_url')}podcast",
            # Add other necessary endpoints
        }
        self.episode_processor = self.get_episode_processor()
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {self.authenticator.get_token()['access_token']}'})

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

    def build_embed(self, url: str, title: str) -> str:
        """
        Builds the HTML embed code for a Podbean episode.

        :param url: The Podbean episode URL containing the 'i' parameter.
        :param title: The title of the episode.
        :return: A string containing the HTML iframe embed code.
        """
        url_params = url.split('&')
        id_param = ''
        for param in url_params:
            if param.startswith('i='):
                id_param = param
                break

        if not id_param:
            self.logger.error(f"Failed to extract 'i' parameter from URL: {url}")
            raise PodbeanEpisodeError(f"Missing 'i' parameter in URL: {url}")

        embed_code = (
            f'<iframe title="{title}" allowtransparency="true" height="150" width="100%" '
            f'style="border: none; min-width: min(100%, 430px);height:150px;" scrolling="no" '
            f'data-name="pb-iframe-player" src="https://www.podbean.com/player-v2/?from=embed&{id_param}'
            f'&share=1&download=1&fonts=Arial&skin=f6f6f6&font-color=auto&rtl=0&logo_link='
            f'&btn-skin=3267a3&size=150" loading="lazy"></iframe>'
        )
        self.logger.debug(f"Generated embed code: {embed_code}")
        return embed_code

    def get_episodes(self, limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Retrieve a list of episodes from Podbean.

        :param limit: Number of episodes to retrieve.
        :return: JSON response containing episodes or None if failed.
        """
        episodes = []
        params = {'limit': limit}
        count = int(self.session.get(self.urls['episodes'], params=params).json()['count'])

        while len(episodes) < count:
            try:
                response = self.session.get(self.urls['episodes'], params=params)
                response.raise_for_status()
                episodes.extend(response.json()['episodes'])
                
                if not response.json()['has_more']:
                    break

            except requests.RequestException as e:
                self.logger.error(f"Error fetching episodes: {e}")
                return None
            
        return episodes[:count]
        

    def get_latest_episode_details(self) -> Optional[Dict[str, Any]]:
        """
        Get details of the latest episode.

        :return: Details of the latest episode or None if unavailable.
        """
        episodes_data = self.get_episodes(1)
        if episodes_data and 'episodes' in episodes_data and episodes_data['episodes']:
            return episodes_data['episodes'][0]
        self.logger.warning("No episodes found.")
        return None