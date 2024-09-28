# Podbean Client

This project provides a Python client to interact with the Podbean API for uploading and managing podcast episodes. It reads from a configuration file located at `~/.config/podbean/config.ini` or `config.ini` in the project directory.

When the client is run manually, the client looks for audio files in an unpublished folder to be uploaded to podbean, which then moves the unpublished audio file to a published folder for organization.

The client can be expanded to work as a service checking if audio needs to be published based on a newly streamed video. For example, within our church, we livestream our service to YouTube and edit the sermon to be a seperate video. With the goal of data backups, the podbean client can check if there is a new livestream or video every day. If there is a new livestream that does not match one the videos in the backup folder, it will automatically download it. If there is a new sermon video uploaded, it will download the video to an edited folder and go through the process of stripping the audio to upload to podcast platforms with the podbean client.

The goal is automation and modularity. If there is another video service that you prefer to use, the client can be expanded with the use of the `config.ini` to account for other platforms.

## TODO
- Restructure/refactor project accordingly
- Integrate Youtube API for full automation
- Ensure testing and errors are raised when specific requirements are not met
- Ensure setup.py works correctly
- Create documentation