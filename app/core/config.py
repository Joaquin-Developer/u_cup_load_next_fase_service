import os
from pydantic_settings import BaseSettings


env = os.getenv("ENV") or "development"
env_dir = os.getenv("ENV_DIR") or os.getcwd()


class Config(BaseSettings):
    ENVIRONMENT: str
    DATABASE_DSN: str
    PRINCIPAL_API_URL: str

    class Config:
        env_file = ".env"


config = Config(_env_file=f"{env_dir}/environments/.env.{env}", ENVIRONMENT=env)
