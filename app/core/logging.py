import sys
from loguru import logger


def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level}</level> | "
               "<cyan>{name}:{function}:{line}</cyan> - "
               "<level>{message}</level>",
    )
    logger.add("logs/app.log", rotation="5 MB", retention="10 days", level="INFO")
    return logger
