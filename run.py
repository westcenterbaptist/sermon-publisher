#! venv/bin/python3.11

import argparse
from podbean_client.podbean.episode import Episode
from podbean_client.podbean.authenticate import PodbeanAuthenticator
from podbean_client.utils.config_manager import ConfigManager
from podbean_client.utils.utils import end_with_slash
from podbean_client.youtube.youtube import YouTubeAPI

class PodbeanClient():
    def __init__(self):
        self.config = ConfigManager().config
        self.urls = self.setup_podbean_urls()

    def setup_podbean_urls(self):
        base_url = end_with_slash(self.config['base_url'])

        urls = {
            'token': base_url + 'oauth/token',
            'auth_upload': base_url + 'files/uploadAuthorize',
            'episodes': base_url + 'episodes',
            'podcast_id': base_url + 'podcast'
        }

        return urls

    def run(self, platform):
        video_description = None
        if platform == 'youtube':
            yt = YouTubeAPI(
                self.config.get('youtube_api_key'),
                self.config.get('youtube_channel'),
                self.config.get('youtube_channel_id'),
            )
            if self.config.get('latest_stream') == True:
                yt.get_video_from_playlist(
                    self.config.get('stream_playlist'),
                    self.config.get('stream_path'),
                )
            if self.config.get('latest_video') == True:
                video_description = yt.get_video_from_playlist(
                    self.config.get('video_playlist'),
                    self.config.get('video_path'),
                    self.config.get('publish_video'),
                    self.config.get('unpublished_audio_path'),
                    self.config.get('published_audio_path')
                )

        if video_description:
            self.config['episode_content'] += f'<p>{video_description}</p>'

        authenticator = PodbeanAuthenticator(
                self.config.get('podbean_api_key'),
                self.config.get('podbean_api_secret'),
                self.urls['token'],
        )
        access_token = authenticator.get_token()['access_token']

        episode = Episode(
            self.config.get('unpublished_audio_path'),
            self.config.get('published_audio_path'),
            self.config.get('podcast_image_path'),
            self.config.get('episode_content'),
            self.config.get('publish_audio'),
            self.urls,
            access_token
        )
        episode.process_unpublished_files()
        authenticator.remove_token()

def parse_args():
    parser = argparse.ArgumentParser(description="Podbean Audio Publishing Client")

    parser.add_argument(
        '-y', '--youtube', 
        action='store_true',
        help='Check YouTube for a new video to upload audio to Podbean'
    )

    return parser.parse_args()

if __name__ == '__main__':
    client = PodbeanClient()
    args = parse_args()

    if args.youtube:
        client.run('youtube')
    else:
        client.run(None)