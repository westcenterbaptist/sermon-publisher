import requests
from sermon_publisher.podbean.episode import Episode
from sermon_publisher.podbean.authenticate import PodbeanAuthenticator
from sermon_publisher.utils.helpers import end_with_slash
from sermon_publisher.utils.config_manager import ConfigManager

class Podbean():
    def __init__(self):
        self.config = ConfigManager().config
        self.base_url = end_with_slash(self.config.get('podbean_api_url'))
        self.urls = self.setup_podbean_urls()
        self.authenticator = self.setup_podbean_auth()
        self.token = self.authenticator.get_token()['access_token']

    def setup_podbean_urls(self):
        urls = {
            'token': self.base_url + 'oauth/token',
            'auth_upload': self.base_url + 'files/uploadAuthorize',
            'episodes': self.base_url + 'episodes',
            'podcast_id': self.base_url + 'podcast'
        }
        return urls

    def setup_podbean_auth(self):
        return PodbeanAuthenticator(
                self.config.get('podbean_api_key'),
                self.config.get('podbean_api_secret'),
                self.urls['token'],
        )

    def setup_podbean_episode(self, token):
        return Episode(
            self.config.get('unpublished_audio_path'),
            self.config.get('published_audio_path'),
            self.config.get('podcast_image_path'),
            self.config.get('episode_content'),
            self.config.get('publish_audio'),
            self.urls,
            self.token
        )

    def publish_podbean_episode(self):
        episode = self.setup_podbean_episode()
        episode.process_unpublished_files()

    def get_podbean_episodes(self, limit=1):
        params = {
            'access_token': self.token,
            'limit': limit
        }
        response = requests.get(self.urls['episodes'], params=params)
        return response.json()
    
    def get_latest_episode_details(self):
        return self.get_podbean_episodes()['episodes'][0]

    def build_embed(self, url, title):
        url_params = url.split('&')
        for param in url_params:
            if param[0] == 'i' and param[1] == '=':
                id = param
        
        return f'<iframe title="{title}" allowtransparency="true" height="150" width="100%" style="border: none; min-width: min(100%, 430px);height:150px;" scrolling="no" data-name="pb-iframe-player" src="https://www.podbean.com/player-v2/?from=embed&{id}&share=1&download=1&fonts=Arial&skin=f6f6f6&font-color=auto&rtl=0&logo_link=&btn-skin=3267a3&size=150" loading="lazy"></iframe>'