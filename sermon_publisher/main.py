# sermon_publisher/main.py

import argparse
import logging
from sermon_publisher.workflows.workflow import Workflow
from sermon_publisher.utils.config_manager import ConfigManager
from sermon_publisher.utils.logging_config import setup_logging
from sermon_publisher.exceptions.custom_exceptions import SermonPublisherError

def parse_args():
    parser = argparse.ArgumentParser(description="Sermon Publisher Client")

    parser.add_argument(
        '-y', '--youtube', 
        action='store_true',
        help='Publish YouTube sermons to Podbean'
    )
    parser.add_argument(
        '-p', '--podbean',
        action='store_true',
        help='Publish episodes to Podbean'
    )
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Run all publishing tasks'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
    )

    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(args.log_level)

    logger = logging.getLogger("SermonPublisherMain")
    logger.info("Starting Sermon Publisher")

    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        return

    try:
        workflow = Workflow(config)
    except SermonPublisherError as e:
        logger.error(f"Workflow initialization failed: {e}", exc_info=True)
        return

    try:
        if args.all:
            workflow.run_all()
        else:
            if args.youtube:
                workflow.publish_all_youtube_sermons_to_website()
            if args.podbean:
                workflow.publish_podbean_episode()
    except SermonPublisherError as e:
        logger.error(f"An error occurred during workflow execution: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)

    logger.info("Sermon Publisher finished.")

if __name__ == "__main__":
    main()
