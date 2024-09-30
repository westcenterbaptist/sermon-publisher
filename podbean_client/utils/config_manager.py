import os
import configparser

class ConfigManager:
    def __init__(self):
        self.config = self.parse_config()

    def parse_config(self):
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
            'podbean_api_key': config.get('PODBEAN_API', 'podbean_api_key', fallback=None),
            'podbean_api_secret': config.get('PODBEAN_API', 'podbean_api_secret', fallback=None),
            'youtube_api_key': config.get('YOUTUBE_API', 'youtube_api_key', fallback=None),
            'youtube_channel': config.get('YOUTUBE_API', 'youtube_channel', fallback=None),
            'youtube_channel_id': config.get('YOUTUBE_API', 'youtube_channel_id', fallback=None),
            'base_url': config.get('PODBEAN_API', 'base_url', fallback=None),
            'unpublished_audio_path': config.get('PATHS', 'unpublished_audio_path', fallback=None),
            'published_audio_path': config.get('PATHS', 'published_audio_path', fallback=None),
            'podcast_image_path': config.get('PATHS', 'podcast_image_path', fallback=None),
            'stream_path': config.get('PATHS', 'stream_path', fallback=None),
            'video_path': config.get('PATHS', 'video_path', fallback=None),
            'publish_audio': config.getboolean('OPTIONS', 'publish_audio', fallback=False),
            'publish_video': config.getboolean('OPTIONS', 'publish_video', fallback=False),
            'episode_content': config.get('OPTIONS', 'episode_content', fallback=None),
            'latest_stream': config.getboolean('OPTIONS', 'latest_stream', fallback=False),
            'latest_video': config.getboolean('OPTIONS', 'latest_video', fallback=False),
            'stream_playlist': config.get('OPTIONS', 'stream_playlist', fallback=None),
            'video_playlist': config.get('OPTIONS', 'video_playlist', fallback=None),
        }

        for key, value in config_vars.items():
            if value == 'None':
                config_vars[key] = None
            if value == 'True':
                config_vars[key] = True

        return config_vars
