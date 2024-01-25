import os
import configparser

class ConfigManager:
    def __init__(self):
        self.config = self.parse_config()

    def parse_config(self):
        config = configparser.ConfigParser()
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, '.config', 'podbean', 'config.ini')
        config.read(config_path)

        config_vars = {
            'api_key': config.get('General', 'api_key'),
            'api_secret': config.get('General', 'api_secret'),
            'unpublished_path': config.get('General', 'unpublished_path'),
            'published_path': config.get('General', 'published_path'),
            'podcast_image_path': config.get('General', 'podcast_image_path'),
            'publish': config.getboolean('General', 'publish'),
            'token_path': config.get('General', 'token_path'),
            'base_url': config.get('General', 'base_url'),
            'episode_content': config.get('General', 'episode_content')
        }

        return config_vars
