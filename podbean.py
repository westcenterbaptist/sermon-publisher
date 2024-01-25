#!/opt/homebrew/bin/python3

from podcast import Podcast
from config_manager import ConfigManager
from authenticate import Authenticator

def main():
    config_manager = ConfigManager()
    config = config_manager.config

    authenticator = Authenticator(config)
    authenticator.authenticate()

    podcast = Podcast(config)
    podcast.process_unpublished_files()

if __name__ == "__main__":
    main()
