import requests
from requests.auth import HTTPBasicAuth
from sermon_publisher.utils.config_manager import ConfigManager
from sermon_publisher.utils.utils import convert_to_iso

class Sermon():
    def __init__(self):
        self.config = ConfigManager().config
        self.base_url = self.config.get('aswp_url')
        self.auth = HTTPBasicAuth(self.config.get('aswp_username'), self.config.get('aswp_app_password'))
        self.sermon_book = self.get_taxonomy_terms("sermon_book")

    def get_sermons(self):
        return requests.get(f"{self.base_url}/sermons")

    def post_youtube_sermon(self, youtube_video, podbean_embed):
        video_id = youtube_video['snippet']['resourceId']['videoId']
        description = youtube_video['snippet']['description'].split('\n')
        title = description[0]
        slug = title.replace(' ', '-').lower()
        
        if self.check_sermon_exists_by_slug(slug):
            return

        image_url = youtube_video['snippet']['thumbnails']['maxres']['url']
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'

        bible_passage = description[1]
        if bible_passage[1] == ' ':
            tmp = bible_passage.split(' ')
            book_name = tmp[0] + ' ' + tmp[1] 
        else:
            book_name = bible_passage.split(' ')[0]

        series_name = description[2].split(':')[1][1:]
        speaker_name = description[3]
        book = self.get_book_value(book_name)
        speaker = self.get_or_create_speaker(speaker_name)
        series = self.get_or_create_sermon_series(series_name)
        date = convert_to_iso(description[4])
        media_id = self.search_media_by_filename(series_name)

        if media_id == None:
            image = self.download_image(image_url)
            media_id = self.upload_image_to_wordpress(image, series_name)

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
        except Exception as e:
            print(f'HTTP Error: Could not publish sermon to website: {e}')

    def get_taxonomy_terms(self, taxonomy):
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

                # Check for successful response
                if response.status_code == 200:
                    terms = response.json()
                    all_terms.extend(terms)

                    # Check if we've retrieved all pages
                    total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                    if page >= total_pages:
                        break  # All pages have been fetched
                    else:
                        page += 1  # Move to the next page
                else:
                    print(f"Failed to fetch terms: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                return None

        return {term['name']: term['id'] for term in all_terms}

    def get_book_value(self, book):
        for k,v in self.sermon_book.items():
            if k == book:
                return v
        return None

    def download_image(self, image_url):
        """
        Downloads an image from the given URL.

        :param image_url: URL of the image to download.
        :return: Tuple containing image content and filename, or (None, None) if failed.
        """
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            # Extract filename from URL
            filename = image_url.split('/')[-1].split('?')[0]  # Handles URLs with query params

            # Validate content type
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                print(f"The URL does not point to an image. Content-Type: {content_type}")
                return None, None

            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Failed to download image: {e}")
            return None, None

    def search_media_by_filename(self, filename):
        """
        Searches the WordPress Media Library for an image with the given filename.

        :param filename: The filename to search for.
        :return: Media ID if found, else None.
        """
        try:
            params = {
                'search': filename,
                'per_page': 100,  # Maximum allowed per_page value
                'media_type': 'image'
            }
            response = requests.get(f'{self.base_url}/media', params=params, auth=self.auth)
            response.raise_for_status()
            media_items = response.json()

            for item in media_items:
                # WordPress may return media items where the filename is part of the title or slug
                # To ensure exact match, compare the 'slug' or 'source_url'
                if 'slug' in item and filename.lower().replace(' ', '-') in item['slug'].lower():
                    return item['id']
            return None
        except requests.exceptions.RequestException as e:
            print(f"Failed to search media: {e}")
            return None

    def upload_image_to_wordpress(self, image_content, filename):
        """
        Uploads an image to the WordPress Media Library.

        :param image_content: Binary content of the image.
        :param filename: Name of the image file.
        :return: Media ID of the uploaded image, or None if failed.
        """
        headers = {
            'Content-disposition': f'attachment; filename={filename}.jpg',
            'Content-Type': 'image/jpeg',  # Adjust if not JPEG
        }

        try:
            response = requests.post(
                f'{self.base_url}media',
                headers=headers,
                data=image_content,
                auth=self.auth
            )
            response.raise_for_status()
            media_id = response.json().get('id')
            return media_id
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload image: {e}")
            print(f"Response: {response.text}")
            return None

    def get_or_create_sermon_series(self, series_name):
        """
        Retrieves the ID of an existing sermon series by name or creates it if it doesn't exist.

        :param series_name: Name of the sermon series.
        :return: ID of the sermon series, or None if failed.
        """
        # Step 1: Search for existing sermon series
        try:
            params = {
                'search': series_name,
                'per_page': 100,  # Maximum allowed per_page value
            }
            response = requests.get(f'{self.base_url}sermon_series', params=params, auth=self.auth)
            response.raise_for_status()
            series_items = response.json()

            # Exact match check
            for item in series_items:
                if item['name'].lower() == series_name.lower():
                    return item['id']

            # If not found, create the sermon series
            payload = {
                'name': series_name,
                'slug': series_name.replace(' ', '-').lower()
            }
            create_response = requests.post(f'{self.base_url}sermon_series', json=payload, auth=self.auth)
            create_response.raise_for_status()
            new_series = create_response.json()
            return new_series['id']

        except requests.exceptions.RequestException as e:
            print(f"Error in get_or_create_sermon_series for '{series_name}': {e}")
            print(f"Response: {response.text}")
            return None

    def get_or_create_speaker(self, speaker_name):
        try:
            params = {
                'search': speaker_name,
                'per_page': 100,  # Maximum allowed per_page value
            }
            response = requests.get(f'{self.base_url}sermon_speaker', params=params, auth=self.auth)
            response.raise_for_status()
            series_items = response.json()

            # Exact match check
            for item in series_items:
                if item['name'].lower() == speaker_name.lower():
                    return item['id']

            # If not found, create the sermon series
            payload = {
                'name': speaker_name,
                'slug': speaker_name.replace(' ', '-').lower()
            }
            create_response = requests.post(f'{self.base_url}sermon_speaker', json=payload, auth=self.auth)
            create_response.raise_for_status()
            new_series = create_response.json()
            return new_series['id']

        except requests.exceptions.RequestException as e:
            print(f"Error in get_or_create_sermon_series for '{speaker_name}': {e}")
            print(f"Response: {response.text}")
            return None

    def check_sermon_exists_by_slug(self, slug):
        """
        Checks if a sermon with the given slug already exists in WordPress.

        :param slug: The slug of the sermon to check.
        :return: True if the sermon exists, False otherwise.
        """
        try:
            # Define the endpoint with the slug query parameter
            search_endpoint = f'{self.base_url}sermons?slug={slug}'

            # Make the GET request
            response = requests.get(search_endpoint, auth=self.auth)
            response.raise_for_status()

            # Parse the JSON response
            sermons = response.json()

            if sermons:
                return True
            else:
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error checking sermon existence for slug '{slug}': {e}")
            return False  # Alternatively, you might want to handle this differently
