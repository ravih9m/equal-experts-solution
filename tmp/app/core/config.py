import logging
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "equal-experts-solution"
    # Assignment Requirement: Port 8080
    PORT: int = Field(default=8080, env="PORT")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    GITHUB_API_URL: str = "https://api.github.com"

settings = Settings()

# Centralized Logger
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gist-api")