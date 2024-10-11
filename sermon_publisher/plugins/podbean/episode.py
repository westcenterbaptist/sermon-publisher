import os
import logging
import requests
from typing import Dict, Any
from sermon_publisher.exceptions.custom_exceptions import PodbeanEpisodeError
from sermon_publisher.podbean.authenticate import PodbeanAuthenticator

class EpisodeProcessor:
    """
    Handles processing and uploading of Podbean episodes.
    """

    def __init__(
        self, 
        unpublished_audio_path: str, 
        published_audio_path: str, 
        image_path: str, 
        content: str, 
        publish: bool,
        urls: Dict[str, str],
        authenticator: PodbeanAuthenticator
    ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.unpublished_audio_path = unpublished_audio_path
        self.published_audio_path = published_audio_path
        self.image_path = image_path
        self.content = content
        self.publish = publish
        self.urls = urls
        self.authenticator = authenticator
        self.access_token = self.authenticator.access_token

    def process_unpublished_files(self) -> None:
        """
        Processes and uploads all unpublished audio files.
        """
        try:
            files = os.listdir(self.unpublished_audio_path)
            self.logger.debug(f"Found {len(files)} files in unpublished_audio_path.")
        except OSError as e:
            self.logger.error(f"Failed to list directory {self.unpublished_audio_path}: {e}")
            raise PodbeanEpisodeError(f"Failed to list directory {self.unpublished_audio_path}") from e

        for filename in files:
            if filename.lower().endswith('.mp3'):
                filepath = os.path.join(self.unpublished_audio_path, filename)
                self.logger.info(f"Processing file: {filename}")
                try:
                    success = self.upload_audio_file(filepath)
                    if success:
                        self.logger.info(f"File upload successful: {filename}")
                        # Move the file to the published_audio_path
                        new_filepath = os.path.join(self.published_audio_path, filename)
                        os.rename(filepath, new_filepath)
                        self.logger.debug(f"Moved file to {new_filepath}")
                    else:
                        self.logger.warning(f"File upload unsuccessful: {filename}")
                except PodbeanEpisodeError as e:
                    self.logger.error(f"Error processing file {filename}: {e}")

    def upload_audio_file(self, filepath: str) -> bool:
        """
        Uploads an audio file to Podbean.

        :param filepath: Path to the audio file.
        :return: True if upload is successful, False otherwise.
        """
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        self.logger.debug(f"Uploading file: {filename}, Size: {filesize} bytes")

        params = {
            'access_token': self.access_token,
            'filename': filename,
            'filesize': filesize,
            'content_type': 'audio/mpeg'
        }

        try:
            response = requests.get(
                self.urls['auth_upload'],
                params=params
            )
            response.raise_for_status()
            token_data = response.json()
            presigned_url = token_data['presigned_url']
            file_key = token_data['file_key']
            self.logger.debug(f"Received presigned URL for {filename}")
        except requests.RequestException as e:
            self.logger.error(f"Failed to retrieve file upload authorization for {filename}: {e}")
            return False
        except KeyError as e:
            self.logger.error(f"Missing key in upload authorization response: {e}")
            return False

        self.logger.info(f"Uploading file {filename} to AWS S3.")
        try:
            with open(filepath, 'rb') as f:
                upload_response = requests.put(
                    presigned_url,
                    data=f
                )
            upload_response.raise_for_status()
            self.logger.info(f"Upload successful: {filename}")
        except requests.RequestException as e:
            self.logger.error(f"Failed to upload file to AWS for {filename}: {e}")
            return False

        # Create the episode in Podbean
        title = os.path.splitext(filename)[0].replace('_', ':')
        status = 'publish' if self.publish else 'draft'

        data = {
            'access_token': self.access_token,
            'title': title,
            'content': self.content,
            'status': status,
            'type': 'public',
            'media_key': file_key,
        }

        self.logger.info(f"Creating episode for {title}")
        try:
            post_response = requests.post(
                self.urls['episodes'],
                data=data
            )
            post_response.raise_for_status()
            self.logger.info(f"Episode created successfully: {title}")
            return True
        except requests.RequestException as e:
            self.logger.error(f"Failed to create episode for {title}: {e}")
            return False

    def get_podcast_id(self) -> str:
        """
        Retrieves the podcast ID from Podbean.

        :return: Podcast ID if successful, 'error' otherwise.
        """
        data = {'access_token': self.access_token}

        self.logger.debug("Retrieving podcast ID.")
        try:
            response = requests.post(
                self.urls['podcast_id'],
                data=data
            )
            response.raise_for_status()
            podcast_id = response.json()['podcast']['id']
            self.logger.debug(f"Podcast ID retrieved: {podcast_id}")
            return podcast_id
        except requests.RequestException as e:
            self.logger.error(f"Failed to retrieve podcast ID: {e}")
            return 'error'
        except KeyError as e:
            self.logger.error(f"Missing key in podcast ID response: {e}")
            return 'error'