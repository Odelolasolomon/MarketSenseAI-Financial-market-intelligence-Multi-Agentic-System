"""
Entry point for starting background worker
"""
import asyncio
from src.services.data_collector import DataCollector
from src.config.settings import get_settings
from src.utilities.logger import get_logger, setup_logging

logger = get_logger(__name__)
settings = get_settings()


async def main_async():
    """Async main function"""
    logger.info("=" * 60)
    logger.info("MULTI-ASSET AI - BACKGROUND WORKER")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Collection Interval: {settings.data_update_interval}s")
    logger.info("=" * 60)
    
    collector = DataCollector()
    
    try:
        await collector.start(interval=settings.data_update_interval)
    except KeyboardInterrupt:
        logger.info("Worker shutdown requested")
        collector.stop()
    except Exception as e:
        logger.error(f"Worker error: {str(e)}", exc_info=True)
        collector.stop()
    finally:
        logger.info("Background worker stopped")


def main():
    """Start the background worker"""
    # Setup logging
    setup_logging()
    
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")


if __name__ == "__main__":
    main()
