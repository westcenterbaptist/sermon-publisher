# podbean-client
The client is built to read from a file located here `~/.config/podbean/config.ini`. Likely will update this in the future to allow customization of a config file, but the correct variable needs to be set up to be read from.

These include:
- api_key (from podbean)
- api_secret (from podbean)
- unpublished_path (unpublished audio folder path)
- published_path (published audio folder path)
- podcast_image_path (still in dev)
- publish (boolean to publish immediately or not)
- token_path (path to podbean token generated)
- base_url (base API url)
- episode_content (HTML for podcast description)
