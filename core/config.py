from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "Enterprise E-Commerce API"

    API_V1_STR: str = "/api/v1"

    STRIPE_API_KEY: str = ""

    JWT_SECRET: str = "change-this-secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()