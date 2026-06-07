from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    telegram_token: str
    models_dir: str = "./models"
    temp_dir: str = "./temp_audio"
    ffmpeg_path: str = "ffmpeg"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
