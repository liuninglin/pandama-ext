import environ

root = environ.Path(__file__) - 4
env = environ.Env()
env.read_env(env_file=root('env/.env.dev'))

from config.settings.base import * 