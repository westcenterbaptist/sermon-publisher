#! venv/bin/python3.12

import argparse
import logging
from sermon_publisher.workflows.workflow import Workflow
from sermon_publisher.utils.config_manager import ConfigManager
from sermon_publisher.utils.logging_config import setup_logging
from sermon_publisher.exceptions.custom_exceptions import SermonPublisherError

class SermonPublisher():
    def __init__(self):
        self.config = ConfigManager().config
        return

    def run(self):
        workflow = Workflow()
        #workflow.download_latest_stream()
        #workflow.download_latest_video()
        #workflow.download_latest_audio()
        #workflow.publish_podbean_episode()
        workflow.publish_all_youtube_sermons_to_website()
        #workflow.publish_latest_youtube_sermon_to_website()

#def parse_args():
#    parser = argparse.ArgumentParser(description="Podbean Audio Publishing Client")
#
#    parser.add_argument(
#        '-y', '--youtube', 
#        action='store_true',
#        help='Check YouTube for a new video to upload audio to Podbean'
#    )
#
#    return parser.parse_args()

if __name__ == '__main__':
    client = SermonPublisher()
    client.run()