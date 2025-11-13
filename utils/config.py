from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    line_channel_access_token: str
    line_channel_secret: str
    log_level: str = "INFO"
    port: int = 8080

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

def get_settings() -> Settings:
    return Settings()
