# Sermon Publisher

A Python application that automates the publishing of sermons to Podbean and YouTube, integrating seamlessly with the Advanced Sermons WP plugin for WordPress. Streamline your content distribution workflow with ease and efficiency.

## Table of Contents

- [Sermon Publisher](#sermon-publisher)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Configuration File](#configuration-file)
  - [Example Usage](#example-usage)
  - [Testing](#testing)
  - [Contributing](#contributing)

## Features

- **Podbean Integration**: Automatically publish audio episodes to Podbean.
- **YouTube Integration**: Download and manage YouTube videos and audio streams.
- **Advanced Sermons Pro WP Integration**: Post sermons directly to your WordPress website using the Advanced Sermons WP plugin.
- **Flexible Workflows**: Customize publishing tasks via command-line arguments.
- **Robust Error Handling**: Comprehensive logging and error management for reliable operations.
- **Secure Configuration**: Manage sensitive information securely within the `config.ini` file.
- **Modular Architecture**: Easily extend the application with additional plugins or workflows.

## Prerequisites

- Python 3.8 or higher
- [FFmpeg](https://ffmpeg.org/download.html) (required for audio processing)

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/sermon_publisher.git
    cd sermon_publisher
    ```

2. **Create a Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Install FFmpeg**

    - **Ubuntu/Debian:**

        ```bash
        sudo apt-get update
        sudo apt-get install ffmpeg
        ```

    - **macOS (using Homebrew):**

        ```bash
        brew install ffmpeg
        ```

    - **Windows:**

        Download the [FFmpeg build](https://ffmpeg.org/download.html), extract it, and add the `bin` directory to your system's PATH.

## Configuration

All configuration settings are managed through the `config/config.ini` file. Ensure that this file is properly configured with your specific details.

### Configuration File

Modify the `config/config.ini` file with your specific settings:

```ini
# config/config.ini

[PODBEAN_PLUGIN]
podbean_api_key = your_podbean_api_key
podbean_api_secret = your_podbean_api_secret
base_url = https://api.podbean.com/v1/
unpublished_audio_path = /path/to/unpublished/audio
published_audio_path = /path/to/published/audio
podbean_image_path = /path/to/podbean/logo.png
episode_content = <p>Podcast episode content</p>
publish_audio = True

[YOUTUBE_PLUGIN]
youtube_api_key = your_youtube_api_key
youtube_channel = your_youtube_channel_name
youtube_channel_id = UCxxxxxxxxxxxxxxxxx
unedited_video_path = /path/to/unedited/videos
edited_video_path = /path/to/edited/videos
stream_playlist = Live Streams
video_playlist = Sermons
publish_video_audio = True

[ADVANCED_SERMONS_WP_PLUGIN]
aswp_url = https://yourwebsite.com/wp-json/wp/v2/
aswp_username = your_wp_username
aswp_app_password = your_wp_app_password

[OPTIONS]
podbean = True
youtube = True
advanced_sermons = True
```

**Security Note:** Ensure that the `config.ini` file contains your actual API keys and secrets. Do not commit this file to version control systems like GitHub to prevent exposing sensitive information. You can add `config/config.ini` to your `.gitignore` file.

## Example Usage

TODO

## Testing

TODO

## Contributing

TODO