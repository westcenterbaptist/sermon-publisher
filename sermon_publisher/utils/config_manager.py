import os
import configparser
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages configuration settings for the application
    """

    def __init__(self):
        self.config = self._parse_config()
        self._validate_config()

    def _parse_config(self) -> Dict[str, Any]:
        """
        Internal function to parse config.ini file for project

        :return: Returns the config variables in python format
        :rtype: Dict[str, Any]
        :raises FileNotFoundError: If the config.ini file cannot be found
        """
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '../../config/config.ini')

        if not os.path.exists(config_path):
            logger.error(f"[-] Config file not found at {config_path}")
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        config.read(config_path)
        logger.debug(f"[*] Loaded configuration from {config_path}")

        config_vars = {
            # PODBEAN_PLUGIN
            'podbean_api_key': config.get('PODBEAN_PLUGIN', 'podbean_api_key', fallback=None),
            'podbean_api_secret': config.get('PODBEAN_PLUGIN', 'podbean_api_secret', fallback=None),
            'podbean_api_url': config.get('PODBEAN_PLUGIN', 'podbean_api_url', fallback=None),
            'unpublished_audio_path': config.get('PODBEAN_PLUGIN', 'unpublished_audio_path', fallback=None),
            'published_audio_path': config.get('PODBEAN_PLUGIN', 'published_audio_path', fallback=None),
            'podbean_image_path': config.get('PODBEAN_PLUGIN', 'podbean_image_path', fallback=None),
            'episode_content': config.get('PODBEAN_PLUGIN', 'episode_content', fallback=None),
            'publish_audio': config.getboolean('PODBEAN_PLUGIN', 'publish_audio', fallback=False),

            # YOUTUBE_PLUGIN
            'youtube_api_key': config.get('YOUTUBE_PLUGIN', 'youtube_api_key', fallback=None),
            'youtube_channel': config.get('YOUTUBE_PLUGIN', 'youtube_channel', fallback=None),
            'youtube_channel_id': config.get('YOUTUBE_PLUGIN', 'youtube_channel_id', fallback=None),
            'unedited_video_path': config.get('YOUTUBE_PLUGIN', 'unedited_video_path', fallback=None),
            'edited_video_path': config.get('YOUTUBE_PLUGIN', 'edited_video_path', fallback=None),
            'stream_playlist': config.get('YOUTUBE_PLUGIN', 'stream_playlist', fallback=None),
            'video_playlist': config.get('YOUTUBE_PLUGIN', 'video_playlist', fallback=None),
            'publish_video_audio': config.getboolean('YOUTUBE_PLUGIN', 'publish_video', fallback=False),

            # ADVANCED_SERMONS_WP_PLUGIN
            'aswp_url': config.get('ADVANCED_SERMONS_WP_PLUGIN', 'aswp_url', fallback=False),
            'aswp_username': config.get('ADVANCED_SERMONS_WP_PLUGIN', 'aswp_username', fallback=False),
            'aswp_app_password': config.get('ADVANCED_SERMONS_WP_PLUGIN', 'aswp_app_password', fallback=False),

            # OPTIONS
            'podbean': config.getboolean('OPTIONS', 'podbean', fallback=False),
            'youtube': config.getboolean('OPTIONS', 'youtube', fallback=False),
            'advanced_sermons': config.getboolean('OPTIONS', 'advanced_sermons', fallback=False),
        }

        for key, value in config_vars.items():
            if isinstance(value, str):
                lowered = value.lower()
                if lowered == 'none':
                    config_vars[key] = None
                elif value == 'true':
                    config_vars[key] = True
                elif value == 'false':
                    config_vars[key] = False
        
        logger.debug("[*] Configuration variables parsed successfully.")
        return config_vars

    def _validate_config(self):
        """
        Validates the loaded configuration to ensure all required settings are present.
        """
        if self.config.get('youtube'):
            if not self.config.get('youtube_channel') and not self.config.get('youtube_channel_id'):
                logger.error("[-] Channel or Channel ID must be configured to use YouTube API.")
                raise ValueError("Channel or Channel ID must be configured to use YouTube API.")
            if not self.config.get('youtube_api_key'):
                logger.error("[-] YouTube API Key must be configured to use YouTube API.")
                raise ValueError("YouTube API Key must be configured to use YouTube API.")

        if self.config.get('podbean'):
            if not self.config.get('podbean_api_key'):
                logger.error("[-] Podbean API Key does not exist, check config.")
                raise ValueError("Podbean API Key does not exist, check config.")
            if not self.config.get('podbean_api_secret'):
                logger.error("[-] Podbean API Secret does not exist, check config.")
                raise ValueError("Podbean API Secret does not exist, check config.")

        if self.config.get('advanced_sermons'):
            if not self.config.get('aswp_url'):
                logger.error("[-] ASWP URL not given, check config.")
                raise ValueError('ASWP URL not given, check config.')
            if not self.config.get('aswp_username'):
                logger.error("[-] ASWP Username not given, check config.")
                raise ValueError('ASWP Username not given, check config.')
            if not self.config.get('aswp_app_password'):
                logger.error("[-] ASWP Password not given, check config.")
                raise ValueError('ASWP Password not given, check config.')

        logger.debug("[*] Configuration validated successfully.")