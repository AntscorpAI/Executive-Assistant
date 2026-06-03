from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Sage AI", alias="APP_NAME")
    environment: str = Field(default="local", alias="ENVIRONMENT")
    use_remote_stack: bool = Field(default=False, alias="USE_REMOTE_STACK")
    database_url: str = Field(default="postgresql+psycopg://sage:sage@localhost:5432/sage", alias="DATABASE_URL")
    database_url_remote: str | None = Field(default=None, alias="DATABASE_URL_REMOTE")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    default_llm_provider: str = Field(default="ollama", alias="DEFAULT_LLM_PROVIDER")
    ollama_url: str | None = Field(default=None, alias="OLLAMA_URL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_url_remote: str | None = Field(default=None, alias="OLLAMA_URL_REMOTE")
    ollama_base_url_remote: str | None = Field(default=None, alias="OLLAMA_BASE_URL_REMOTE")
    ollama_chat_model: str = Field(default="llama3.1:8b", alias="OLLAMA_CHAT_MODEL")
    ollama_chat_model_remote: str | None = Field(default=None, alias="OLLAMA_CHAT_MODEL_REMOTE")
    ollama_embedding_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBEDDING_MODEL")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_url_remote: str | None = Field(default=None, alias="QDRANT_URL_REMOTE")
    whatsapp_gateway_url: str | None = Field(default=None, alias="WHATSAPP_GATEWAY_URL")
    whatsapp_gateway_token: str | None = Field(default=None, alias="WHATSAPP_GATEWAY_TOKEN")
    ms_teams_webhook_url: str | None = Field(default=None, alias="MS_TEAMS_WEBHOOK_URL")
    email_from: str = Field(default="sage@example.com", alias="EMAIL_FROM")
    ms_graph_tenant_id: str | None = Field(default=None, alias="MS_GRAPH_TENANT_ID")
    ms_graph_client_id: str | None = Field(default=None, alias="MS_GRAPH_CLIENT_ID")
    ms_graph_client_secret: str | None = Field(default=None, alias="MS_GRAPH_CLIENT_SECRET")
    ms_graph_user_id: str | None = Field(default=None, alias="MS_GRAPH_USER_ID")
    jwt_issuer: str = Field(default="sage-ai", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="sage-users", alias="JWT_AUDIENCE")
    initial_admin_email: str = Field(default="admin@example.com", alias="INITIAL_ADMIN_EMAIL")
    initial_admin_password: str = Field(default="change-me", alias="INITIAL_ADMIN_PASSWORD")
    initial_admin_full_name: str = Field(default="System Admin", alias="INITIAL_ADMIN_FULL_NAME")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def active_database_url(self) -> str:
        if self.use_remote_stack and self.database_url_remote:
            return self.database_url_remote
        return self.database_url

    @property
    def active_ollama_base_url(self) -> str:
        if self.use_remote_stack and self.ollama_url_remote:
            return self.ollama_url_remote
        if self.use_remote_stack and self.ollama_base_url_remote:
            return self.ollama_base_url_remote
        if self.ollama_url:
            return self.ollama_url
        return self.ollama_base_url

    @property
    def active_ollama_chat_model(self) -> str:
        if self.use_remote_stack and self.ollama_chat_model_remote:
            return self.ollama_chat_model_remote
        return self.ollama_chat_model

    @property
    def active_qdrant_url(self) -> str:
        if self.use_remote_stack and self.qdrant_url_remote:
            return self.qdrant_url_remote
        return self.qdrant_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
