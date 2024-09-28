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
            'podbean_api_key': config.get('PODBEAN_API', 'podbean_api_key'),
            'podbean_api_secret': config.get('PODBEAN_API', 'podbean_api_secret'),
            'base_url': config.get('PODBEAN_API', 'base_url'),
            'unpublished_audio_path': config.get('PATHS', 'unpublished_audio_path'),
            'published_audio_path': config.get('PATHS', 'published_audio_path'),
            'podcast_image_path': config.get('PATHS', 'podcast_image_path'),
            'token_path': config.get('PATHS', 'token_path'),
            'publish': config.getboolean('OPTIONS', 'publish'),
            'episode_content': config.get('OPTIONS', 'episode_content'),
        }

        return config_vars
