import asyncio
from modules.db.models import init_db
from loguru import logger


# Запуск сервиса
async def start_all_services():
    try:
        await init_db()
    except KeyboardInterrupt:
        logger.info("Сессия приостановлена")

    logger.info("Сервисы запущены!")
    pass


if __name__ == "__main__":
    asyncio.run(start_all_services())
