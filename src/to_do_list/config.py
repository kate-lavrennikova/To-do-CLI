from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    USER: str
    PASS: str
    DB_NAME: str

    @property
    def database_url(self):
        return f"postgresql+psycopg://{self.USER}:{self.PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
