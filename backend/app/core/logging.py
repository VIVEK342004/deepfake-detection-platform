import logging
import sys
from backend.app.core.config import settings

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Silence overly verbose external loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)

logger = logging.getLogger("deepfake_platform")
