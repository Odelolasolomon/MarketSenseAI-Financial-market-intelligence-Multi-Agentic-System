"""
Entry point for starting the API server
"""
import uvicorn
from src.config.settings import get_settings
from src.utilities.logger import get_logger, setup_logging

logger = get_logger(__name__)
settings = get_settings()


def main():
    """Start the FastAPI server"""
    # Setup logging
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("MULTI-ASSET AI - API SERVER")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    logger.info("=" * 60)
    
    try:
        uvicorn.run(
            "src.adapters.web.fastapi_app:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
    finally:
        logger.info("API server stopped")


if __name__ == "__main__":
    main()