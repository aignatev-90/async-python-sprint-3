from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str = ''
    APP_PORT: int = 0
    APP_PROTO: str = ''
    USERS_DB: str = ''
    MAIN_CHAT_DB: str = ''

    class Config:
        case_sensitive = False
        env_file = 'vars.env'
