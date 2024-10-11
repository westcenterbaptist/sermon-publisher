class SermonPublisherError(Exception):
    """Base exception for Sermon Publisher errors."""
    pass

class WorkflowError(SermonPublisherError):
    """Exception raised for errors in the workflow."""
    pass

class PluginInitializationError(SermonPublisherError):
    """Exception raised for plugin initialization failures."""
    pass

class YouTubeAPIError(SermonPublisherError):
    """Exception raised for YouTube API related errors."""
    pass

class SermonWPError(SermonPublisherError):
    """Exception raised for Advanced Sermons WP related errors."""
    pass
