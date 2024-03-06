from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    USER: str
    PASS: str
    DB_NAME: str
    MODE: str

    @property
    def database_url(self):
        return f"postgresql+psycopg://{self.USER}:{self.PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".dev.env")

settings = Settings()
