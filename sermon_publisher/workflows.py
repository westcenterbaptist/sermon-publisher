from sermon_publisher.youtube import YouTubeAPI

class Workflow():
    def __init__(self, config) -> None:
        self.config = config
        self.yt = YouTubeAPI(
            self.config.get('youtube_api_key'),
            self.config.get('youtube_channel'),
            self.config.get('youtube_channel_id'),
        )

    def download_latest_stream(self):
        self.yt.get_video_from_playlist(
            self.config.get('stream_playlist'),
            self.config.get('unedited_video_path'),
        )
    
    def publish_video_audio(self):
        return self.yt.get_video_from_playlist(
            self.config.get('video_playlist'),
            self.config.get('edited_video_path'),
            self.config.get('publish_video'),
            self.config.get('unpublished_audio_path'),
            self.config.get('published_audio_path')
        )