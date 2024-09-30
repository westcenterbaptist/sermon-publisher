#! venv/bin/python3.11

#import argparse
from sermon_publisher.utils.config_manager import ConfigManager
from sermon_publisher.workflows import Workflow
from sermon_publisher.podbean.publish import publish_podcast
class SermonPublisher():
    def __init__(self):
        self.config = ConfigManager().config
        self.video_description = None

    def run(self):
        if self.config['youtube']:
            workflow = Workflow(self.config)
            workflow.download_latest_stream()
            self.video_description = workflow.publish_video_audio()

        if self.video_description:
            self.config['episode_content'] += f'<p>{self.video_description}</p>'

        if self.config['podbean']:
            publish_podcast(self.config)


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