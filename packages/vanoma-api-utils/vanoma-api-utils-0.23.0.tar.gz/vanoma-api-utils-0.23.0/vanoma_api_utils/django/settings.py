import os
import dj_database_url  # type: ignore
from typing import Any, Dict
from ..misc import resolve_environment


def resolve_database() -> Dict[str, str]:
    if resolve_environment() == "testing":
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join("/tmp", "db.sqlite3"),
        }

    return dj_database_url.config(conn_max_age=600)


def resolve_logging() -> Dict[str, Any]:
    if resolve_environment() == "testing":
        return {}

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
