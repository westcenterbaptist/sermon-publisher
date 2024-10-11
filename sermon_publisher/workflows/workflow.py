# sermon_publisher/workflows/workflow.py

from typing import Dict, Any, Optional
import logging

from sermon_publisher.workflows.strategies.publish_youtube_sermons import PublishYouTubeSermonsStrategy
from sermon_publisher.workflows.strategies.publish_podbean_episode import PublishPodbeanEpisodeStrategy
from sermon_publisher.workflows.base_workflow import BaseWorkflow
from sermon_publisher.exceptions.custom_exceptions import WorkflowError
from sermon_publisher.plugins.plugin_factory import PluginFactory

class Workflow(BaseWorkflow):
    """
    Orchestrates publishing tasks by utilizing various strategies.
    """

    def __init__(self, config: Dict[str, Any], factory: Optional[PluginFactory] = None):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        factory = factory or PluginFactory(config)
        try:
            self.youtube_api = factory.create_youtube_api()
            self.podbean_client = factory.create_podbean_client()
            self.sermon = factory.create_sermon()
        except WorkflowError as e:
            self.logger.error(f"Plugin initialization failed: {e}")
            raise WorkflowError("Failed to initialize plugins.") from e

        if not any([self.youtube_api, self.podbean_client, self.sermon]):
            self.logger.warning("No plugins are enabled in the configuration.")

        # Initialize strategies
        self.strategies = []
        if self.youtube_api and self.sermon:
            self.strategies.append(
                PublishYouTubeSermonsStrategy(
                    youtube_api=self.youtube_api,
                    sermon=self.sermon,
                    config=self.config
                )
            )
        if self.podbean_client:
            episode_processor = self.podbean_client.get_episode_processor()
            self.strategies.append(
                PublishPodbeanEpisodeStrategy(
                    episode_processor=episode_processor,
                    config=self.config
                )
            )

        self.logger.debug(f"Initialized with {len(self.strategies)} strategies.")

    def run_all(self) -> None:
        """
        Executes all available publishing tasks using strategies.
        """
        if not self.strategies:
            self.logger.warning("No strategies to execute.")
            return

        for strategy in self.strategies:
            try:
                strategy.execute()
                self.logger.info(f"Executed strategy: {strategy.__class__.__name__}")
            except WorkflowError as e:
                self.logger.error(f"Strategy {strategy.__class__.__name__} failed: {e}", exc_info=True)

    def publish_all_youtube_sermons_to_website(self) -> None:
        """
        Executes the strategy to publish all YouTube sermons to the website.
        """
        strategy = next((s for s in self.strategies if isinstance(s, PublishYouTubeSermonsStrategy)), None)
        if strategy:
            try:
                strategy.execute()
                self.logger.info(f"Executed strategy: {strategy.__class__.__name__}")
            except WorkflowError as e:
                self.logger.error(f"Strategy {strategy.__class__.__name__} failed: {e}", exc_info=True)
        else:
            self.logger.warning("PublishYouTubeSermonsStrategy is not available.")

    def publish_podbean_episode(self) -> None:
        """
        Executes the strategy to publish a Podbean episode.
        """
        strategy = next((s for s in self.strategies if isinstance(s, PublishPodbeanEpisodeStrategy)), None)
        if strategy:
            try:
                strategy.execute()
                self.logger.info(f"Executed strategy: {strategy.__class__.__name__}")
            except WorkflowError as e:
                self.logger.error(f"Strategy {strategy.__class__.__name__} failed: {e}", exc_info=True)
        else:
            self.logger.warning("PublishPodbeanEpisodeStrategy is not available.")