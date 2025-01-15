import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(env: str, name: Optional[str] = None) -> None:
    root_logger = logging.getLogger(name)
    root_logger.setLevel(logging.INFO) if env == 'production' else root_logger.setLevel(logging.DEBUG)

    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    logs_file = logs_dir / "app.log"

    # Добавляем обработчик ротации
    handler = TimedRotatingFileHandler(
        filename=logs_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)


