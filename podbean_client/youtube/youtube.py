import os
import googleapiclient.discovery
import yt_dlp

class YouTubeAPI():
    def __init__(
        self, 
        api_key,
        channel, 
        channel_id,
    ):
        if channel == None and channel_id == None:
            raise Exception('Channel or Channel ID must be configured to use YouTube API')
        if api_key == None:
            raise Exception('YouTube API Key must be configured to use YouTube API')

        self.yt = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
        self.channel = channel

        if channel_id:
            self.channel_id = channel_id
        else:
            self.channel_id = self.get_channel_id()
            print(f'Channel ID for Config: {self.channel_id}')

        self.playlists = self.list_playlists()

    def get_video_from_playlist(
        self, playlist, save_path,
        publish=False, unpublished_audio_path=None,
        published_audio_path=None
    ):
        playlist = self.get_playlist(playlist)
        playlist_id = playlist['id']
        video = self.get_playlist_video(playlist_id)
        video_title = video['snippet']['title'].replace(':','_')
        video_id = video['snippet']['resourceId']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video_description = video['snippet']['description'].replace('\n','<br/>')

        ydl_opts = {
            'outtmpl': f'{save_path}/{video_title}',  # Output path and filename template
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # Force MP4 video and audio
            'merge_output_format': 'mp4',  # Ensure final output is MP4
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if publish == True:
            if not os.path.exists(f'{published_audio_path}/{video_title}.mp3'):
                ydl_opts = {
                    'format': 'bestaudio/best',  # Download the best available audio
                    'outtmpl': f'{unpublished_audio_path}/{video_title}',  # Output template
                    'postprocessors': [{  # Use ffmpeg to convert the audio to mp3
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',  # Set the quality (bitrate) of the MP3
                    }],
                }
    
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])

        return video_description

    def get_channel_id(self):
        if self.channel == None:
            raise Exception('Channel must be configured to find Channel ID')
            
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
        for playlist in self.playlists:
            if playlist['snippet']['title'] == key:
                return playlist
        raise Exception('Streaming Playlist Not Found')

    def get_playlist_video(self, playlist_id):
        request = self.yt.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=1,  # Only fetch the latest video
        )

        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]
        else:
            raise Exception('ERROR: Could not retrieve video from playlist')

    def channel_error(self):
        raise Exception('Channel ID not found, ensure the channel is configured correctly')


