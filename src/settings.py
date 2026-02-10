from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    debug: bool

    openrouter_base_url: str
    openrouter_api_key: SecretStr

    openrouter_model_1: str
    openrouter_model_2: str
    openrouter_model_3: str
