import logging
from typing import Dict, Any
from sermon_publisher.workflows.strategies.base_strategy import BaseStrategy
from sermon_publisher.exceptions.custom_exceptions import WorkflowError

class PublishPodbeanEpisodeStrategy(BaseStrategy):
    """
    Strategy for publishing episodes to Podbean.
    """

    def __init__(self, episode_processor: Any, config: Dict[str, Any]):
        self.episode_processor = episode_processor
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self) -> None:
        """
        Executes the publishing of Podbean episodes.
        """
        try:
            self.logger.info("Processing unpublished Podbean audio files.")
            self.episode_processor.process_unpublished_files()
            self.logger.info("Podbean episodes processed successfully.")
        except Exception as e:
            self.logger.error(f"Failed to publish Podbean episode: {e}", exc_info=True)
            raise WorkflowError("Error in publishing Podbean episode.") from e