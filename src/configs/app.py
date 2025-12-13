from dynaconf import Dynaconf
from pydantic import BaseModel


class APPConfig(BaseModel):
    app_version: str
    app_name: str
    app_host: str
    app_port: int


class DBConfig(BaseModel):
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    @property
    def dsl(self):
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def dsl_test(self):
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@localhost:{self.db_port}/{self.db_name}"
        )

    @property
    def dsn(self) -> str:
        return self.dsl


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int


class RedisConfig(BaseModel):
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str


class Settings(BaseModel):
    app: APPConfig
    db: DBConfig
    auth: AuthConfig
    redis: RedisConfig


env_settings = Dynaconf(settings_file=["settings.toml"])

settings = Settings(
    app=env_settings["app_settings"],
    db=env_settings["db_settings"],
    auth=env_settings["auth_settings"],
    redis=env_settings["redis_settings"],
)
