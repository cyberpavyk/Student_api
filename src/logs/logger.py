from loguru import logger


logger.add(
    'src/logs/debug.log',
    level="DEBUG",
    rotation="50 MB",
    compression='zip',
    enqueue=True,
    backtrace=True,
    diagnose=True,
    format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {message}"
    )
