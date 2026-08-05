"""FastAPI application entry point."""

from src.core.config import create_application
from src.core.logger import configure_logging
from src.core.settings import get_settings

settings = get_settings()
configure_logging(settings)
app = create_application(settings)
