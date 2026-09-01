from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    POSTGRES_USER: str = "agrotrace"
    POSTGRES_PASSWORD: str = "agrotrace_dev"
    POSTGRES_DB: str = "agrotrace"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

settings = Settings()
