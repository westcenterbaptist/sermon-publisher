import os
import googleapiclient.discovery
import yt_dlp
from sermon_publisher.utils.config_manager import ConfigManager

class YouTubeAPI():
    def __init__(self):
        self.config = ConfigManager().config
        self.channel = self.config.get('youtube_channel')
        self.channel_id = self.get_channel_id()
        self.api_key = self.config.get('youtube_api_key')

        try:
            self.yt = googleapiclient.discovery.build("youtube", "v3", developerKey=self.api_key)
        except Exception as e:
            print(f'Could not setup YouTube client. Check API Key.\n{e}')
            raise

    def _download(self, download_video, video, save_path):
        title = video['snippet']['title'].replace(':','_')
        id = video['id']
        url = f'https://www.youtube.com/watch?v={id}'

        if download_video == False:
            if os.path.exists(f'{save_path}/{title}.mp3'):
                return
            opts = {
                'format': 'bestaudio/best',  # Download the best available audio
                'outtmpl': f'{save_path}/{title}',  # Output template
                'postprocessors': [{  # Use ffmpeg to convert the audio to mp3
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',  # Set the quality (bitrate) of the MP3
                }],
            }
        else:
            opts = {
                'outtmpl': f'{save_path}/{title}',  # Output path and filename template
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # Force MP4 video and audio
                'merge_output_format': 'mp4',  # Ensure final output is MP4
            }

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    def download_latest_video(self, playlist, save_path):
        id = self.get_playlist_id(playlist)
        video = self.get_playlist_videos(id, 1)
        self._download(True, video, save_path)

    def download_latest_audio(self, playlist, save_path):
        id = self.get_playlist_id(playlist)
        video = self.get_playlist_videos(id, 1)
        self._download(False, video, save_path)

    def download_audio(self, video_id, save_path):
        video = self.get_video_by_id(video_id)
        print(video)
        self._download(False, video, save_path)

    def get_video_by_id(self, id):
        request = self.yt.videos().list(
            part='snippet',
            id=id
        )
        response = request.execute()

        if not response['items']:
            return None
        
        return response['items'][0]


    def get_playlist_id(self, playlist):
        return self.get_playlist(playlist)['id']

    def get_channel_id(self):
        if self.channel == None:
            raise Exception('Channel must be configured to find Channel ID')
        
        if self.config.get('youtube_channel_id'):
            return self.config.get('youtube_channel_id')
            
        request = self.yt.search().list(
            part='snippet',
            q=self.channel,
            type='channel',
            maxResults=1
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]['snippet']['channelId']
        else:
            self.channel_error()

    def list_playlists(self):
        if not self.channel_id:
            self.channel_error()

        request = self.yt.playlists().list(
            part='snippet',
            channelId=self.channel_id,
            maxResults=25
        )
        response = request.execute()
        return response['items']

    def get_playlist(self, key):
        playlists = self.list_playlists()
        for playlist in playlists:
            if playlist['snippet']['title'] == key:
                return playlist
        raise Exception('Streaming Playlist Not Found')

    def get_playlist_videos(self, playlist_id, count=1):
        videos = []
        next_page = None

        while True:
            request = self.yt.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=count,
                pageToken=next_page
            )

            response = request.execute()
            if 'items' in response and len(response['items']) > 0:
                videos.extend(response['items'])
            else:
                raise Exception('ERROR: Could not retrieve video from playlist')

            next_page = response.get('nextPageToken')
            if not next_page:
                break

        return videos

    def get_playlist_video_count(self, playlist_id):
        request = self.yt.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=1
        )

        try:
            response = request.execute()
            return response['pageInfo']['totalResults']
        except Exception as e:
            print(f'HTTP ERROR: Could not retrieve video count: {e}')
            raise

    def get_video_description(self, video):
        return video['snippet']['description']

    def get_latest_youtube_video_description(self):
        return self.get_latest_video_details()['snippet']['description']

    def get_latest_video_details(self):
        id = self.get_playlist_id(self.config.get('video_playlist'))
        return self.get_playlist_videos(id, 1)[0]

    def get_all_youtube_videos_from_playlist(self, playlist):
        id = self.get_playlist_id(playlist)
        count = self.get_playlist_video_count(id)
        return self.get_playlist_videos(id, count)

    def channel_error(self):
        raise Exception('Channel ID not found, ensure the channel is configured correctly')