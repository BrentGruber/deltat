from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Delta T API"

    ENVIRONMENT: str = "PRODUCTION"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    LOGLEVEL: str = "warning"

    class Config:
        case_sensitive = True


settings = Settings()