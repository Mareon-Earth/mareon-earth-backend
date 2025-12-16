import logging
import sys
from app.core.config import get_settings


def setup_logging():
    """
    Configure the root logger based on settings.
    Call this in main.py before starting the app.
    """
    settings = get_settings()

    # Map string level to logging constant
    level_str = settings.log_level.upper()
    level = getattr(logging, level_str, logging.INFO)

    handlers = [logging.StreamHandler(sys.stdout)]

    # Basic JSON formatter configuration (if libraries like python-json-logger are not present)
    # If you install python-json-logger, replace this logic with JsonFormatter
    if settings.json_logs:
        # Simple fallback or specific JSON logic could go here
        # For now, we stick to standard logging but ensure the stream is correct
        pass

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

    # Optional: silence noisy third-party libraries if needed
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
