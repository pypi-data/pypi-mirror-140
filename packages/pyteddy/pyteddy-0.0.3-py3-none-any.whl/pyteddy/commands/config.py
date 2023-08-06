import shelve
from pathlib import Path

DB_NAME = str(Path(__file__).parent / 'config')
config_entries = ('user_name', 'user_email', 'organisation')


def config(args):
    with shelve.open(DB_NAME) as db:
        for key, value in args.items():
            if key in config_entries:
                db[key] = value


def get_config(args):
    with shelve.open(DB_NAME) as db:
        for key, value in args.copy().items():
            if value is None:
                args[key] = db.get(key)
