from sermon_publisher.youtube import YouTubeAPI
from sermon_publisher.advanced_sermons.sermon import Sermon
from sermon_publisher.podbean.podbean import Podbean
from sermon_publisher.utils.config_manager import ConfigManager
from sermon_publisher.utils.utils import strip_break

class Workflow():
    def __init__(self) -> None:
        self.config = ConfigManager().config
        if self.config['youtube']:
            self.yt = YouTubeAPI()
        else:
            self.yt = None

        if self.config['podbean']:
            self.podbean = Podbean()
        else:
            self.podbean = None

        if self.config['advanced_sermons']:
            self.sermon = Sermon()
        else:
            self.sermon = None

    def download_latest_stream(self):
        if self.yt == None:
            raise Exception('Cannot download stream unless Youtube config is correct')
        self.yt.download_video(
            self.config.get('stream_playlist'),
            self.config.get('unedited_video_path'),
        )

    def download_latest_video(self):
        if self.yt == None:
            raise Exception('Cannot download video unless Youtube config is correct')
        self.yt.download_video(
            self.config.get('video_playlist'),
            self.config.get('edited_video_path')
        )

    def download_latest_audio(self):
        if self.yt == None:
            raise Exception('Cannot download audio unless YouTube config is correct')
        self.yt.download_audio(
            self.config.get('video_playlist'),
            self.config.get('published_audio_path')
        )
    
    def get_youtube_video_description(self):
        if self.yt == None:
            raise Exception('Cannot obtain video description unless YouTube config is correct.')
        video = self.yt.get_video_details(self.config.get('video_playlist'))
        return self.yt.get_video_description(video)

    def publish_youtube_sermon_to_website(self):
        podbean_details = self.podbean.get_latest_episode()['episodes'][0]
        podbean_embed = self.podbean.build_embed(podbean_details['player_url'], podbean_details['title'])
        self.sermon.post_youtube_sermon(podbean_details, podbean_embed) 

    def publish_podbean_episode(self):
        if self.config['youtube']:
            self.config['episode_content'] += f'<p>{self.get_youtube_video_description()}</p>'
        self.podbean.publish_podbean_episode()