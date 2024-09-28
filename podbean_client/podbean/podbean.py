from podbean_client.podbean.podcast import Podcast
from podbean_client.utils.config_manager import ConfigManager
from podbean_client.podbean.authenticate import Authenticator

class PodbeanClient():
    def __init__(self):
        self.config = ConfigManager().config
        self.authenticator = Authenticator(self.config)
        self.podcast = Podcast(self.config)

    def run(self):
        self.authenticator.authenticate()
        self.podcast.process_unpublished_files()