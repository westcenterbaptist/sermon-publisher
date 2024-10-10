import requests
from requests.auth import HTTPBasicAuth
from sermon_publisher.utils.config_manager import ConfigManager

class Sermon():
    def __init__(self):
        self.config = ConfigManager().config
        self.base_url = self.config.get('aswp_url')
        self.auth = HTTPBasicAuth(self.config.get('aswp_username'), self.config.get('aswp_app_password'))
        self.sermon_series = self.get_taxonomy_terms("sermon_series")
        self.sermon_speaker = self.get_taxonomy_terms("sermon_speaker")
        self.sermon_topics = self.get_taxonomy_terms("sermon_topics")
        self.sermon_book = self.get_taxonomy_terms("sermon_book")

    def get_sermons(self):
        return requests.get(f"{self.base_url}/sermons")

    def post_youtube_sermon(self, podbean_details, podbean_embed):
        title = podbean_details['title'].split('–')[0][:-1]
        slug = title.replace(' ', '-').lower()

        payload = {
            "title": title,
            "slug": slug,
            "status": "draft"
        }

        #response = requests.post(f"{self.base_url}/sermons", auth=self.auth, json=data)

    def get_taxonomy_terms(self, taxonomy):
        response = requests.get(f"{self.base_url}/{taxonomy}", auth=self.auth)
        if response.status_code == 200:
            return {term['name']: term['id'] for term in response.json()}
        else:
            print(f"Error fetching {taxonomy} terms: {response.status_code}")
            return {}
