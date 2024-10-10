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

    def _download(self, video, playlist, save_path):
        video = self.get_video_details(playlist)
        title = video['snippet']['title'].replace(':','_')
        id = video['snippet']['resourceId']['videoId']
        url = f'https://www.youtube.com/watch?v={id}'
        description = self.get_video_description(video)

        if video == False:
            if not os.path.exists(f'{save_path}/{title}.mp3'):
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

    def download_video(self, playlist, save_path):
        self._download(True, playlist, save_path)

    def download_audio(self, playlist, save_path):
        self._download(False, playlist, save_path)

    def get_video_details(self, playlist):
        playlist = self.get_playlist(playlist)
        playlist_id = playlist['id']
        video = self.get_playlist_video(playlist_id)
        return video

    def get_video_description(self, video):
        return video['snippet']['description'].replace('\n','<br/>')

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

    def get_playlist_video(self, playlist_id, count=1):
        request = self.yt.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=count,  # Only fetch the latest video
        )

        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]
        else:
            raise Exception('ERROR: Could not retrieve video from playlist')

    def channel_error(self):
        raise Exception('Channel ID not found, ensure the channel is configured correctly')