import os
import time
import requests
from authenticate import Authenticator

class Podcast:
    def __init__(self, config):
        self.config = config
        self.authenticator = Authenticator(config)
        self.token = self.authenticator.read_token()
        self.image = self.config['podcast_image_path']
        self.content = self.config['episode_content']

    def process_unpublished_files(self):
        # Loop over files in unpublished_path and upload them
        for filename in os.listdir(self.config['unpublished_path']):
            if filename.endswith('.mp3'):
                filepath = os.path.join(self.config['unpublished_path'], filename)
                res = self.upload_audio_file(filepath)
                if res:
                    print(f"File upload successful: {filename}")
                    # Move the file to the published_path
                    new_filepath = os.path.join(self.config['published_path'], filename)
                    os.rename(filepath, new_filepath)
                else:
                    print(f"File upload unsuccessful: {filename}")

    def upload_audio_file(self, filepath):
        filename = os.path.basename(filepath)
        auth_file_url = f"{self.config['base_url']}files/uploadAuthorize"
        params = {
            'access_token': self.token,
            'filename': filename,
            'filesize': int(os.path.getsize(filepath)),
            'content_type': 'audio/mpeg'
        }

        response = requests.get(
        auth_file_url,
        params=params
        )
    
        if response.status_code == 200:
            presigned_url = response.json()['presigned_url']
            expire_at = response.json()['expire_at']
            file_key = response.json()['file_key']
        else:
            print("Failed to retrieve file upload authorization")
            return False

        print("Uploading file...may take a minute...")

        response = requests.put(
            presigned_url,
            data=open(filepath, 'rb')
        )

        if not response.status_code == 200:
            print("Failed to upload file to AWS")
            return False
        
        print("Upload Successful!")

        episode_url = f"{self.config['base_url']}episodes"
        title = filename.split('.')[0]
        title = title.replace('_', ':')

        if self.config['publish']:
            status = 'publish'
        else:
            status = 'draft'

        data = {
           'access_token': self.token,
           'title': title,
           'content': self.content,
           'status': status,
           'type': 'public',
           'media_key': file_key,
#           'logo_key': self.image,
        }

        print("Creating Episode!")

        response = requests.post(
            episode_url,
            data=data
        )

        if not response.status_code == 200:
            print(response.json())
            return False

        return True

    def get_podcast_id(self):
        podcast_url = f"{self.config['base_url']}podcast"

        data = {'access_token': self.token}

        response = requests.post(
            podcast_url,
            data=data
        )

        if response.status_code == 200:
            return response.json()['podcast']['id']

        return 'error'
