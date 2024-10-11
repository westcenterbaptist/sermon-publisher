import os
import logging
from typing import Dict, Any, Optional, List
import googleapiclient.discovery
import yt_dlp
from sermon_publisher.exceptions.custom_exceptions import YouTubeAPIError

class YouTubeAPI:
    """
    A client for interacting with the YouTube API.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        :param config: The config from ConfigManager() in main.py
        :type config: Dict[str, Any]
        :return: Class object of YouTubeAPI
        :raises YouTubeAPIError: If the API Key is not found
        :raises YouTubeAPIError: If the YouTube client cannot be initialized
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.channel = self.config.get('youtube_channel')
        self.channel_id = self.get_channel_id()
        self.api_key = self.config.get('youtube_api_key')

        if not self.api_key:
            self.logger.error("YouTube API key is missing.")
            raise YouTubeAPIError("YouTube API key is required.")

        try:
            self.yt = googleapiclient.discovery.build("youtube", "v3", developerKey=self.api_key)
            self.logger.debug("YouTube client initialized successfully.")
        except Exception as e:
            self.logger.error(f"Could not setup YouTube client. Check API Key.\n{e}")
            raise YouTubeAPIError("Failed to initialize YouTube client.") from e

    def _download(self, download_video: bool, video: Dict[str, Any], save_path: str) -> None:
        """
        An internally called function to handle all downloading, video or audio

        :param boolean download_video: True to download video, False to download audio
        :param Dict[str, Any] video: YouTube video passed for downloading media
        :param str save_path: The file path to save the media to
        :rtype: None
        :raises YouTubeAPIError: If the download fails
        """
        title = video['snippet']['title'].replace(':', '_')
        video_id = video['id']
        url = f'https://www.youtube.com/watch?v={video_id}'

        if not download_video:
            if os.path.exists(f'{save_path}/{title}.mp3'):
                self.logger.info(f"[*] Audio already exists: {title}.mp3")
                return
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{save_path}/{title}',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
        else:
            if os.path.exists(f'{save_path}/{title}.mp4'):
                self.logger.info(f"[*] Video already exists: {title}.mp4")
                return
            opts = {
                'outtmpl': f'{save_path}/{title}',
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
            }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
                if download_video:
                    self.logger.info(f"[+] Video downloaded: {title}.mp4")
                else:
                    self.logger.info(f"[+] Audio downloaded: {title}.mp3")
            except Exception as e:
                self.logger.error(f"[-] Failed to download {'video' if download_video else 'audio'} for {title}: {e}")
                raise YouTubeAPIError(f"Download failed for {title}") from e

    def download_latest_video(self, playlist: str, save_path: str) -> None:
        """
        External function used to download the latest video given a YouTube playlist.

        :param str playlist: YouTube playlist name
        :param str save_path: File path to save media to
        :rtype: None
        """
        playlist_id = self.get_playlist_id(playlist)
        video = self.get_playlist_videos(playlist_id, 1)
        self._download(True, video[0], save_path)

    def download_latest_audio(self, playlist: str, save_path: str) -> None:
        """
        External function used to download the latest video given a YouTube playlist.

        :param str playlist: YouTube playlist name
        :param str save_path: File path to save media to
        :rtype: None
        """
        playlist_id = self.get_playlist_id(playlist)
        video = self.get_playlist_videos(playlist_id, 1)
        self._download(False, video[0], save_path)

    def download_audio(self, video_id: str, save_path: str) -> None:
        """
        External function used to download the audio given a YouTube video ID.

        :param str video_id: YouTube video ID
        :param str save_path: File path to save media to
        :rtype: None
        """
        video = self.get_video_by_id(video_id)
        if video:
            self._download(False, video, save_path)
        else:
            self.logger.warning(f"[-] Video with ID {video_id} not found.")

    def download_video(self, video_id: str, save_path: str) -> None:
        """
        External function used to download the video given a YouTube video ID.

        :param str video_id: YouTube video ID
        :param str save_path: File path to save media to
        :rtype: None
        """
        video = self.get_video_by_id(video_id)
        if video:
            self._download(True, video, save_path)
        else:
            self.logger.warning(f"[-] Video with ID {video_id} not found.")

    def get_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        request = self.yt.videos().list(part='snippet', id=video_id)
        response = request.execute()

        if not response['items']:
            self.logger.warning(f"No video found with ID: {video_id}")
            return None

        self.logger.debug(f"Video details retrieved for ID: {video_id}")
        return response['items'][0]

    def get_playlist_id(self, playlist_name: str) -> str:
        playlist = self.get_playlist(playlist_name)
        return playlist['id']

    def get_channel_id(self) -> str:
        if not self.channel:
            self.logger.error('Channel must be configured to find Channel ID')
            raise YouTubeAPIError('Channel must be configured to find Channel ID')

        if self.config.get('youtube_channel_id'):
            self.logger.debug("Using provided YouTube channel ID.")
            return self.config.get('youtube_channel_id')

        request = self.yt.search().list(part='snippet', q=self.channel, type='channel', maxResults=1)
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            channel_id = response['items'][0]['snippet']['channelId']
            self.logger.debug(f"Found channel ID: {channel_id}")
            return channel_id
        else:
            self.logger.error('Channel ID not found, ensure the channel is configured correctly')
            raise YouTubeAPIError('Channel ID not found, ensure the channel is configured correctly')

    def list_playlists(self) -> List[Dict[str, Any]]:
        if not self.channel_id:
            self.logger.error('Channel ID is not available.')
            raise YouTubeAPIError('Channel ID is not available.')

        request = self.yt.playlists().list(part='snippet', channelId=self.channel_id, maxResults=25)
        response = request.execute()
        self.logger.debug(f"Fetched {len(response.get('items', []))} playlists.")
        return response.get('items', [])

    def get_playlist(self, playlist_name: str) -> Dict[str, Any]:
        playlists = self.list_playlists()
        for playlist in playlists:
            if playlist['snippet']['title'] == playlist_name:
                self.logger.debug(f"Found playlist '{playlist_name}' with ID: {playlist['id']}")
                return playlist
        self.logger.error(f'Playlist "{playlist_name}" not found.')
        raise YouTubeAPIError(f'Playlist "{playlist_name}" not found.')

    def get_playlist_videos(self, playlist_id: str, count: int = 1) -> List[Dict[str, Any]]:
        videos = []
        next_page = None

        while len(videos) < count:
            request = self.yt.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=min(count - len(videos), 50),
                pageToken=next_page
            )

            response = request.execute()
            items = response.get('items', [])

            if not items:
                self.logger.warning('Could not retrieve video from playlist.')
                break

            videos.extend(items)
            self.logger.debug(f"Fetched {len(items)} videos from playlist.")

            next_page = response.get('nextPageToken')
            if not next_page:
                break

        if not videos:
            self.logger.error('No videos retrieved from the playlist.')
            raise YouTubeAPIError('No videos retrieved from the playlist.')

        return videos[:count]

    def get_playlist_video_count(self, playlist_id: str) -> int:
        request = self.yt.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=1
        )

        try:
            response = request.execute()
            count = response['pageInfo']['totalResults']
            self.logger.debug(f"Total videos in playlist {playlist_id}: {count}")
            return count
        except Exception as e:
            self.logger.error(f'Could not retrieve video count for playlist {playlist_id}: {e}')
            raise YouTubeAPIError(f'Could not retrieve video count: {e}') from e

    def get_video_description(self, video: Dict[str, Any]) -> str:
        return video['snippet']['description']

    def get_latest_youtube_video_description(self) -> str:
        latest_video = self.get_latest_video_details()
        return self.get_video_description(latest_video) if latest_video else ''

    def get_latest_video_details(self) -> Optional[Dict[str, Any]]:
        playlist_id = self.get_playlist_id(self.config.get('video_playlist'))
        videos = self.get_playlist_videos(playlist_id, 1)
        return videos[0] if videos else None

    def get_all_youtube_videos_from_playlist(self, playlist: str) -> List[Dict[str, Any]]:
        playlist_id = self.get_playlist_id(playlist)
        video_count = self.get_playlist_video_count(playlist_id)
        return self.get_playlist_videos(playlist_id, video_count)
