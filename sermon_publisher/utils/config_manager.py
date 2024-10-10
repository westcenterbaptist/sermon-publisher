import os
import configparser

class ConfigManager:
    def __init__(self):
        self.config = self._parse_config()
        self._check_config()

    def _parse_config(self):
        config = configparser.ConfigParser()
        home_dir = os.path.expanduser("~")
        custom_config_path = os.path.join(home_dir, '.config', 'podbean', 'config.ini')
        current_path = os.path.dirname(__file__)
        default_config_path = os.path.join(current_path, '../../config.ini')

        if os.path.exists(custom_config_path):
            config.read(custom_config_path)
        elif os.path.exists(default_config_path):
            config.read(default_config_path)
        else:
            raise FileNotFoundError(f"""
            Config file not found. Check one of the two paths below\n
             Custom Path: {custom_config_path}
            Default Path: {default_config_path}
            """)

        config_vars = {
            'podbean_api_key': config.get('PODBEAN_PLUGIN', 'podbean_api_key', fallback=None),
            'podbean_api_secret': config.get('PODBEAN_PLUGIN', 'podbean_api_secret', fallback=None),
            'base_url': config.get('PODBEAN_PLUGIN', 'base_url', fallback=None),
            'unpublished_audio_path': config.get('PODBEAN_PLUGIN', 'unpublished_audio_path', fallback=None),
            'published_audio_path': config.get('PODBEAN_PLUGIN', 'published_audio_path', fallback=None),
            'podbean_image_path': config.get('PODBEAN_PLUGIN', 'podbean_image_path', fallback=None),
            'episode_content': config.get('PODBEAN_PLUGIN', 'episode_content', fallback=None),
            'publish_audio': config.getboolean('PODBEAN_PLUGIN', 'publish_audio', fallback=False),
            'youtube_api_key': config.get('YOUTUBE_PLUGIN', 'youtube_api_key', fallback=None),
            'youtube_channel': config.get('YOUTUBE_PLUGIN', 'youtube_channel', fallback=None),
            'youtube_channel_id': config.get('YOUTUBE_PLUGIN', 'youtube_channel_id', fallback=None),
            'unedited_video_path': config.get('YOUTUBE_PLUGIN', 'unedited_video_path', fallback=None),
            'edited_video_path': config.get('YOUTUBE_PLUGIN', 'edited_video_path', fallback=None),
            'stream_playlist': config.get('YOUTUBE_PLUGIN', 'stream_playlist', fallback=None),
            'video_playlist': config.get('YOUTUBE_PLUGIN', 'video_playlist', fallback=None),
            'publish_video_audio': config.getboolean('YOUTUBE_PLUGIN', 'publish_video', fallback=False),
            'aswp_url': config.get('ADVANCED_SERMONS_WP_PLUGIN', 'aswp_url', fallback=False),
            'aswp_username': config.get('ADVANCED_SERMONS_WP_PLUGIN', 'aswp_username', fallback=False),
            'aswp_app_password': config.get('ADVANCED_SERMONS_WP_PLUGIN', 'aswp_app_password', fallback=False),
            'podbean': config.getboolean('OPTIONS', 'podbean', fallback=False),
            'youtube': config.getboolean('OPTIONS', 'youtube', fallback=False),
            'advanced_sermons': config.getboolean('OPTIONS', 'advanced_sermons', fallback=False),
        }

        for key, value in config_vars.items():
            if value == 'None':
                config_vars[key] = None
            if value == 'True':
                config_vars[key] = True
            if value == 'False':
                config_vars[key] = False
        return config_vars

    def _check_config(self):
        if self.config['youtube']:
            if self.config['youtube_channel'] == None and self.config['youtube_channel_id'] == None:
                raise Exception('Channel or Channel ID must be configured to use YouTube API')
            if self.config['youtube_api_key'] == None:
                raise Exception('YouTube API Key must be configured to use YouTube API')
        if self.config['podbean']:
            if self.config['podbean_api_key'] == None:
                raise Exception("Podbean API Key does not exist, check config.")
            if self.config['podbean_api_secret'] == None:
                raise Exception("Podbean API Secret does not exist, check config.")
        if self.config['advanced_sermons']:
            if self.config['aswp_url'] == None:
                raise Exception('ASWP URL not given, check config.')
            if self.config['aswp_username'] == None:
                raise Exception('ASWP Username not given, check config.')
            if self.config['aswp_app_password'] == None:
                raise Exception('ASWP Password not given, check config')