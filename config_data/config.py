from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    db_url: str


@dataclass
class Config:
    bot: TgBot


def load_config(path: str | None=None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot=TgBot(
            token=env('BOT_TOKEN'),
            db_url=env('DATABASE_SQLITE')
        )
    )