from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_id: int
    db_url: str
    client_id: str
    client_secret: str
    redirect_uri: str


@dataclass
class Config:
    bot: TgBot


def load_config(path: str | None=None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_id=env('ADMIN_ID'),
            db_url=env('DATABASE_SQLITE'),
            client_id=env('CLIENT_ID'),
            client_secret=env('CLIENT_SECRET'),
            redirect_uri=env('REDIRECT_URI')
        )
    )