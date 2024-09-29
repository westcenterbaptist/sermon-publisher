import os
import time
import requests

class Episode():
    def __init__(
        self, 
        unpub_path, 
        pub_path, 
        image_path, 
        content, 
        publish,
        urls,
        token
    ):
        self.unpub = unpub_path
        self.pub = pub_path
        self.image = image_path
        self.content = content
        self.publish = publish
        self.urls = urls
        self.token = token

    def process_unpublished_files(self):
        # Loop over files in unpublished_audio_path and upload them
        for filename in os.listdir(self.unpub):
            if filename.endswith('.mp3'):
                filepath = os.path.join(self.unpub, filename)
                res = self.upload_audio_file(filepath)
                if res:
                    print(f"File upload successful: {filename}")
                    # Move the file to the published_audio_path
                    new_filepath = os.path.join(self.pub, filename)
                    os.rename(filepath, new_filepath)
                else:
                    print(f"File upload unsuccessful: {filename}")

    def upload_audio_file(self, filepath):
        filename = os.path.basename(filepath)

        params = {
            'access_token': self.token,
            'filename': filename,
            'filesize': int(os.path.getsize(filepath)),
            'content_type': 'audio/mpeg'
        }

        response = requests.get(
            self.urls['auth_upload'],
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

        title = filename.split('.')[0]
        title = title.replace('_', ':')

        if self.publish:
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
        }

        print("Creating Episode!")

        response = requests.post(
            self.urls['episodes'],
            data=data
        )

        if not response.status_code == 200:
            print(response.json())
            return False

        return True

    def get_podcast_id(self):
        data = {'access_token': self.token}

        response = requests.post(
            self.urls['podcast_id'],
            data=data
        )

        if response.status_code == 200:
            return response.json()['podcast']['id']

        return 'error'
