from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SIGIT_",
        env_file=".env",
        extra="ignore",
    )

    timeout: int = 15
    max_concurrency: int = 25
    impersonate: str = "chrome124"
    proxy: str | None = None
    veriphone_key: str = "5F2D6300E445DEA88684053144996C"
    isitarealemail_key: str = "0c6ad1fd-f753-4628-8c0a-7968e722c6c7"


settings = Settings()
