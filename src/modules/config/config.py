from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigSettings(BaseSettings):
    db_host: str
    db_port: str
    db_name: str
    db_password: str
    db_user: str
    debug: bool
    model_config = SettingsConfigDict(env_file="deploy/.env")

    def urlconfig(self) -> str:
        db_url = (
            "postgresql+asyncpg://"
            + f"{self.db_user}:{self.db_password}@{self.db_host}"
            + f":{self.db_port}/{self.db_name}"
        )
        return db_url


config = ConfigSettings()

print(config.urlconfig())
