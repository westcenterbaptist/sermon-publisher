# sermon_publisher/plugins/advanced_sermons_wp/sermon.py

import logging
from typing import Dict, Any, Optional
import requests
from requests.auth import HTTPBasicAuth
from sermon_publisher.utils.helpers import convert_to_iso
from sermon_publisher.exceptions.custom_exceptions import SermonWPError

class Sermon:
    """
    Handles interactions with the Advanced Sermons WP plugin.
    """

    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.base_url = self.config.get('aswp_url')
        self.auth = HTTPBasicAuth(self.config.get('aswp_username'), self.config.get('aswp_app_password'))
        self.sermon_book = self.get_taxonomy_terms("sermon_book")

        if not all([self.base_url, self.auth.username, self.auth.password]):
            self.logger.error("ASWP configuration is incomplete.")
            raise SermonWPError("ASWP configuration is incomplete.")

    def get_sermons(self) -> requests.Response:
        return requests.get(f"{self.base_url}/sermons", auth=self.auth)

    def post_youtube_sermon(self, youtube_video: Dict[str, Any], podbean_embed: str) -> None:
        video_id = youtube_video['snippet']['resourceId']['videoId']
        description = youtube_video['snippet']['description'].split('\n')
        title = description[0]
        slug = title.replace(' ', '-').lower()

        if self.check_sermon_exists_by_slug(slug):
            self.logger.info(f"Sermon '{slug}' already exists. Skipping.")
            return

        image_url = youtube_video['snippet']['thumbnails']['maxres']['url']
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'

        bible_passage = description[1]
        if bible_passage.startswith(' '):
            tmp = bible_passage.strip().split(' ')
            book_name = f"{tmp[0]} {tmp[1]}" if len(tmp) > 1 else tmp[0]
        else:
            book_name = bible_passage.split(' ')[0]

        series_name = description[2].split(':')[1].strip() if ':' in description[2] else description[2].strip()
        speaker_name = description[3]
        book = self.get_book_value(book_name)
        speaker = self.get_or_create_speaker(speaker_name)
        series = self.get_or_create_sermon_series(series_name)
        date = convert_to_iso(description[4])
        media_id = self.search_media_by_filename(series_name)

        if media_id is None:
            image_content = self.download_image(image_url)
            media_id = self.upload_image_to_wordpress(image_content, series_name)
            if media_id is None:
                self.logger.error("Failed to upload image. Cannot proceed with sermon posting.")
                return

        meta = {
            'asp_sermon_video_type_select': 'youtube',
            'asp_sermon_youtube': youtube_url,
            'asp_sermon_audio_embed': podbean_embed,
            'asp_sermon_bible_passage': bible_passage,
        }

        payload = {
            'title': title,
            'content': None,
            'slug': slug,
            'status': 'publish',
            'meta': meta,
            'sermon_series': series,
            'sermon_speaker': speaker,
            'sermon_topics': None,
            'sermon_book': book,
            'date': date,
            'featured_media': media_id,
        }

        try:
            response = requests.post(f"{self.base_url}/sermons", auth=self.auth, json=payload)
            response.raise_for_status()
            self.logger.info(f"Sermon '{title}' posted successfully.")
        except requests.RequestException as e:
            self.logger.error(f"HTTP Error: Could not publish sermon to website: {e}")
            raise SermonWPError(f"Could not publish sermon '{title}': {e}") from e

    def get_taxonomy_terms(self, taxonomy: str) -> Dict[str, int]:
        url = f"{self.base_url}/{taxonomy}"
        all_terms = []
        page = 1

        while True:
            params = {
                "per_page": 100,
                "page": page,
                "orderby": "name",
                "order": "asc",
            }

            try:
                response = requests.get(url, params=params, auth=self.auth)
                response.raise_for_status()
                terms = response.json()
                all_terms.extend(terms)

                total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                if page >= total_pages:
                    break
                else:
                    page += 1
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to fetch taxonomy terms: {e}")
                raise SermonWPError(f"Failed to fetch taxonomy terms: {e}") from e

        self.logger.debug(f"Fetched {len(all_terms)} taxonomy terms for '{taxonomy}'.")
        return {term['name']: term['id'] for term in all_terms}

    def get_book_value(self, book: str) -> Optional[int]:
        return self.sermon_book.get(book)

    def download_image(self, image_url: str) -> Optional[bytes]:
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                self.logger.error(f"The URL does not point to an image. Content-Type: {content_type}")
                return None

            self.logger.debug(f"Image downloaded from {image_url}")
            return response.content
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download image: {e}")
            return None

    def search_media_by_filename(self, filename: str) -> Optional[int]:
        try:
            params = {
                'search': filename,
                'per_page': 100,
                'media_type': 'image'
            }
            response = requests.get(f"{self.base_url}/media", params=params, auth=self.auth)
            response.raise_for_status()
            media_items = response.json()

            for item in media_items:
                if 'slug' in item and filename.lower().replace(' ', '-') in item['slug'].lower():
                    self.logger.debug(f"Found existing media ID {item['id']} for filename '{filename}'.")
                    return item['id']
            self.logger.info(f"No existing media found for filename '{filename}'.")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to search media: {e}")
            return None

    def upload_image_to_wordpress(self, image_content: bytes, filename: str) -> Optional[int]:
        if not image_content:
            self.logger.error("No image content to upload.")
            return None

        headers = {
            'Content-Disposition': f'attachment; filename={filename}.jpg',
            'Content-Type': 'image/jpeg',  # Adjust if not JPEG
        }

        try:
            response = requests.post(
                f"{self.base_url}/media",
                headers=headers,
                data=image_content,
                auth=self.auth
            )
            response.raise_for_status()
            media_id = response.json().get('id')
            self.logger.info(f"Uploaded image '{filename}.jpg' with media ID {media_id}.")
            return media_id
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to upload image: {e}")
            self.logger.debug(f"Response: {response.text}")
            return None

    def get_or_create_sermon_series(self, series_name: str) -> Optional[int]:
        try:
            # Search for existing sermon series
            params = {
                'search': series_name,
                'per_page': 100,
            }
            response = requests.get(f"{self.base_url}/sermon_series", params=params, auth=self.auth)
            response.raise_for_status()
            series_items = response.json()

            for item in series_items:
                if item['name'].lower() == series_name.lower():
                    self.logger.debug(f"Found existing sermon series '{series_name}' with ID {item['id']}.")
                    return item['id']

            # Create new sermon series
            payload = {
                'name': series_name,
                'slug': series_name.replace(' ', '-').lower()
            }
            create_response = requests.post(f"{self.base_url}/sermon_series", json=payload, auth=self.auth)
            create_response.raise_for_status()
            new_series = create_response.json()
            self.logger.info(f"Created new sermon series '{series_name}' with ID {new_series['id']}.")
            return new_series['id']

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in get_or_create_sermon_series for '{series_name}': {e}")
            self.logger.debug(f"Response: {response.text}")
            raise SermonWPError(f"Error in get_or_create_sermon_series for '{series_name}': {e}") from e

    def get_or_create_speaker(self, speaker_name: str) -> Optional[int]:
        try:
            # Search for existing speaker
            params = {
                'search': speaker_name,
                'per_page': 100,
            }
            response = requests.get(f"{self.base_url}/sermon_speaker", params=params, auth=self.auth)
            response.raise_for_status()
            speaker_items = response.json()

            for item in speaker_items:
                if item['name'].lower() == speaker_name.lower():
                    self.logger.debug(f"Found existing speaker '{speaker_name}' with ID {item['id']}.")
                    return item['id']

            # Create new speaker
            payload = {
                'name': speaker_name,
                'slug': speaker_name.replace(' ', '-').lower()
            }
            create_response = requests.post(f"{self.base_url}/sermon_speaker", json=payload, auth=self.auth)
            create_response.raise_for_status()
            new_speaker = create_response.json()
            self.logger.info(f"Created new speaker '{speaker_name}' with ID {new_speaker['id']}.")
            return new_speaker['id']

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in get_or_create_speaker for '{speaker_name}': {e}")
            self.logger.debug(f"Response: {response.text}")
            raise SermonWPError(f"Error in get_or_create_speaker for '{speaker_name}': {e}") from e

    def check_sermon_exists_by_slug(self, slug: str) -> bool:
        try:
            search_endpoint = f"{self.base_url}/sermons?slug={slug}"
            response = requests.get(search_endpoint, auth=self.auth)
            response.raise_for_status()
            sermons = response.json()

            exists = bool(sermons)
            if exists:
                self.logger.info(f"Sermon with slug '{slug}' exists.")
            else:
                self.logger.debug(f"Sermon with slug '{slug}' does not exist.")
            return exists

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error checking sermon existence for slug '{slug}': {e}")
            return False