# sermon_publisher/workflows/base_workflow.py

from abc import ABC, abstractmethod

class BaseWorkflow(ABC):
    """
    Abstract base class for all workflows.
    """

    @abstractmethod
    def run_all(self) -> None:
        """
        Executes all tasks in the workflow.
        """
        pass

    @abstractmethod
    def publish_all_youtube_sermons_to_website(self) -> None:
        """
        Publishes all YouTube sermons to the website.
        """
        pass

    @abstractmethod
    def publish_podbean_episode(self) -> None:
        """
        Publishes an episode to Podbean.
        """
        pass
