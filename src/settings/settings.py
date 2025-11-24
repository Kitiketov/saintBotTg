from pydantic_settings import BaseSettings
from pydantic import AnyUrl, field_validator, Field


class Settings(BaseSettings):
    bot_token: str = ""
    chat_id: int | None = Field(default=None, alias="CHAT_ID")

    @field_validator("chat_id", mode="before")
    def _normalize_chat_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
        try:
            return int(v)
        except Exception:
            return None

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
