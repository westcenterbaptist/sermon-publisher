import logging
from typing import Dict, Any
from sermon_publisher.workflows.strategies.base_strategy import BaseStrategy
from sermon_publisher.exceptions.custom_exceptions import WorkflowError

class PublishYouTubeSermonsStrategy(BaseStrategy):
    """
    Strategy for publishing YouTube sermons to the website.
    """

    def __init__(self, youtube_api: Any, sermon: Any, config: Dict[str, Any]):
        self.youtube_api = youtube_api
        self.sermon = sermon
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self) -> None:
        """
        Executes the publishing of all YouTube sermons to the website.
        """
        try:
            self.logger.info("Fetching all YouTube videos from playlist.")
            videos = self.youtube_api.get_all_youtube_videos_from_playlist(self.config.get('video_playlist'))
            self.logger.debug(f"Fetched {len(videos)} videos from YouTube playlist.")

            for video in videos:
                description = self.youtube_api.get_video_description(video)
                self.logger.debug(f"Processing video: {video['snippet']['title']}")
                # Assuming `sermon.post_youtube_sermon` handles matching and posting
                self.sermon.post_youtube_sermon(video, "")  # Pass embed_html if applicable

            self.logger.info("YouTube sermons published successfully.")

        except Exception as e:
            self.logger.error(f"Failed to publish YouTube sermons: {e}", exc_info=True)
            raise WorkflowError("Error in publishing YouTube sermons.") from e
