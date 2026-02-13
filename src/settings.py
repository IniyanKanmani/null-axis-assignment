from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )

    debug: bool

    openrouter_base_url: str
    openrouter_api_key: SecretStr

    openrouter_model_1: str
    openrouter_model_2: str
    openrouter_model_3: str
    openrouter_model_4: str

    model_1_system_prompt_path: str
    model_2_system_prompt_path: str
    model_3_system_prompt_path: str
    model_4_system_prompt_path: str

    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: SecretStr
