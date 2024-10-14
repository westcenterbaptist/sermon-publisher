import logging
from typing import Dict, Any, List
from sermon_publisher.workflows.strategies.base_strategy import BaseStrategy
from sermon_publisher.exceptions.custom_exceptions import WorkflowError
from sermon_publisher.plugins.youtube.api import YouTubeAPI
from sermon_publisher.plugins.podbean.client import PodbeanClient

class PublishYouTubeSermonsStrategy(BaseStrategy):
    """
    Strategy for publishing YouTube sermons to the website.
    """

    def __init__(self, youtube_api: YouTubeAPI, podbean_client: PodbeanClient, sermon: Any, config: Dict[str, Any]):
        self.youtube_api = youtube_api
        self.podbean_client = podbean_client
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
            episodes = self.podbean_client.get_episodes()
            matches = self._find_matches(videos, episodes)

            to_publish = []

            for video in videos:
                vtitle = video['snippet']['title']
                san_vtitle = self._sanitize_title(vtitle)
                if san_vtitle in matches:
                    for episode in episodes:
                        san_etitle = self._sanitize_title(episode['title'])
                        if san_etitle in matches:
                            embed = self.podbean_client.build_embed(episode['player_url'], vtitle)
                            to_publish.append([video, embed])
                            break
                            
            for v in to_publish:
                self.sermon.post_youtube_sermon(v[0], v[1])  # Pass embed_html if applicable
                self.logger.info("YouTube sermons published successfully.")

        except Exception as e:
            self.logger.error(f"Failed to publish YouTube sermons: {e}", exc_info=True)
            raise WorkflowError("Error in publishing YouTube sermons.") from e

    def _find_matches(self, videos: List, episodes: List) -> List:
        vtitles = []
        for video in videos:
            title = self._sanitize_title(video['snippet']['title'])
            vtitles.append(title)

        etitles = []
        for episode in episodes:
            title = self._sanitize_title(episode['title'])
            etitles.append(title)

        return set(vtitles).intersection(etitles)

    def _sanitize_title(self, title: str) -> str:
        title = str(title)
        title = title.lower()
        if '’' in title:
            title = title.replace('’', "'")
        if '-' in title:
            title = title.replace('-', '|')
        if '–' in title:
            title = title.replace('–', '|')
        index = title.find('|')
        if '|' in title and title[index].isalpha():
            title = list(title)
            title[index] = '-'
            title = "".join(title)
        if '|' in title:
            index = title.find('|')
            title = title[:index-1]
        if '?' in title:
            title = title.replace('?', '')
        return title
