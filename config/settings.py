from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    telegram_token: str
    models_dir: str = "./models"
    temp_dir: str = "./temp_audio"

    class Config:
        env_file = ".env"

settings = Settings()
