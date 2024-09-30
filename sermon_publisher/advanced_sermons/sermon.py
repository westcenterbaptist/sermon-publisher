import requests
from requests.auth import HTTPBasicAuth

class Sermon():
    def __init__(self, username, password, url):
        self.url = url
        self.auth = HTTPBasicAuth(username, password)
        print(self.get_sermons())

    def get_sermons(self):
        return requests.get(self.url)

    def post_sermon(self):
        data = {
            "title": "New Sermon Title",
            "content": "This is the sermon content",
            "status": "publish"
        }

        response = requests.post(self.url, auth=self.auth, json=data)

        print(response.status_code)
        print(response.json())