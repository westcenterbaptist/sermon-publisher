class SermonPublisherError(Exception):
    """Base exception for Sermon Publisher errors."""
    pass

class WorkflowError(SermonPublisherError):
    """Exception raised for errors in the workflow."""
    pass

class PluginInitializationError(SermonPublisherError):
    """Exception raised for plugin initialization failures."""
    pass

class PodbeanAuthError(SermonPublisherError):
    """Exception raised for Podbean authentication errors."""
    pass

class PodbeanEpisodeError(SermonPublisherError):
    """Exception raised for Podbean episode processing errors."""
    pass

class PodbeanClientError(SermonPublisherError):
    """Exception raised for Podbean client errors."""
    pass

class YouTubeAPIError(SermonPublisherError):
    """Exception raised for YouTube API related errors."""
    pass

class SermonWPError(SermonPublisherError):
    """Exception raised for Advanced Sermons WP related errors."""
    pass

# Add more specific exceptions as needed
