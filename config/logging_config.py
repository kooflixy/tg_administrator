import logging
from typing import Literal


def logging_configure(level=logging.INFO, filemode: Literal["a", "w"] = "a"):
    logging.getLogger("aiogram.event").setLevel(
        logging.WARNING
    )  # логи aiogram только с logging.WARNING

    # Создание корневого логгера
    logger = logging.getLogger()
    logger.setLevel(level)

    # Файловый хендлер
    file_formatter = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d] %(name)70s:%(lineno)-3s %(levelname)-7s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler("logs.log", mode=filemode, encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(level)

    # Консольный хендлер
    console_formatter = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d] %(levelname)-7s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)

    # Добавляем хендлеры
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
