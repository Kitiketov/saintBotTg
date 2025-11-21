from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    bot_token: str = ""
    chat_id: int = 0


    @property
    def api_base(self) -> AnyUrl:
        """Возвращает адрес API в зависимости от окружения."""
        base: AnyUrl | None = None
        if self.api_env.lower() == "local" and self.api_base_local is not None:
            base = self.api_base_local
        else:
            base = self.api_base_host

        if base is None:
            raise ValueError("API base URL is not configured")

        return base

    class Config:
        env_file = ".env"
