from sermon_publisher.plugins.youtube.api import YouTubeAPI
from sermon_publisher.advanced_sermons.sermon import Sermon
from sermon_publisher.podbean.podbean import Podbean
from sermon_publisher.utils.config_manager import ConfigManager

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
        self.yt.download_latest_video(
            self.config.get('video_playlist'),
            self.config.get('edited_video_path')
        )

    def download_latest_audio(self):
        if self.yt == None:
            raise Exception('Cannot download audio unless YouTube config is correct')
        self.yt.download_latest_audio(
            self.config.get('video_playlist'),
            self.config.get('published_audio_path')
        )

    def publish_latest_youtube_sermon_to_website(self):
        youtube_video = self.yt.get_latest_video_details()
        podbean_episode_details = self.podbean.get_latest_episode_details()
        podbean_embed = self.podbean.build_embed(podbean_episode_details['player_url'], podbean_episode_details['title'])
        print(youtube_video, podbean_embed)
        #self.sermon.post_youtube_sermon(youtube_video, podbean_embed) 

    def publish_all_youtube_sermons_to_website(self):
        videos = self.yt.get_all_youtube_videos_from_playlist(self.config.get('video_playlist'))
        episodes = self.podbean.get_podbean_episodes(1000)['episodes']
        matches = []

        for video in videos:
            description = video['snippet']['description'].split('\n')
            video_title = description[0].lower()
            if '’' in video_title:
                video_title = video_title.replace('’','\'')
            for episode in episodes:
                episode_title = episode['title'].lower()
                if '-' in episode_title:
                    index = episode_title.find('-')
                    episode_title = episode_title[:index-1]
                if '–' in episode_title:
                    index = episode_title.find('–')
                    episode_title = episode_title[:index-1]
                if '’' in episode_title:
                    episode_title = episode_title.replace('’','\'')

                if 'living and lif' in episode_title and 'living and lif' in video_title:
                    matches.append([video, self.podbean.build_embed(episode['player_url'], episode['title'])])
                    episodes.remove(episode)
                    break

                if 'how to be rem' in episode_title and 'how to be rem' in video_title:
                    matches.append([video, self.podbean.build_embed(episode['player_url'], episode['title'])])
                    episodes.remove(episode)
                    break

                if video_title == episode_title:
                    matches.append([video, self.podbean.build_embed(episode['player_url'], episode['title'])])
                    episodes.remove(episode)
                    break

        for pair in matches:
            self.sermon.post_youtube_sermon(pair[0], pair[1])

    def publish_podbean_episode(self):
        if self.config['youtube']:
            youtube_content = self.yt.get_latest_youtube_video_description().replace('\n', '<br/>')
            self.config['episode_content'] += f'<p>{youtube_content}</p>'
        self.podbean.publish_podbean_episode()