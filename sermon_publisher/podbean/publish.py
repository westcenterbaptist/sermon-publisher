from sermon_publisher.podbean.episode import Episode
from sermon_publisher.podbean.authenticate import PodbeanAuthenticator
from sermon_publisher.utils.utils import end_with_slash

def setup_podbean_urls(url):
    base_url = end_with_slash(url)

    urls = {
        'token': base_url + 'oauth/token',
        'auth_upload': base_url + 'files/uploadAuthorize',
        'episodes': base_url + 'episodes',
        'podcast_id': base_url + 'podcast'
    }

    return urls

def publish_podcast(config):
    urls = setup_podbean_urls(config['base_url'])
    authenticator = PodbeanAuthenticator(
            config.get('podbean_api_key'),
            config.get('podbean_api_secret'),
            urls['token'],
    )
    access_token = authenticator.get_token()['access_token']

    episode = Episode(
        config.get('unpublished_audio_path'),
        config.get('published_audio_path'),
        config.get('podcast_image_path'),
        config.get('episode_content'),
        config.get('publish_audio'),
        urls,
        access_token
    )
    episode.process_unpublished_files()
    authenticator.remove_token()