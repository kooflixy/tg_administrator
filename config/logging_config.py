import logging
from typing import Literal

def logging_configure(level=logging.INFO, filemode: Literal['a', 'w'] = 'a'):
    logging.getLogger("aiogram.event").setLevel(logging.WARNING) # логи aiogram только с logging.WARNING

    logging.getLogger("telethon").setLevel(logging.WARNING)

    logging.basicConfig(
        level=level, filename='logs.log', filemode=filemode,
        encoding='utf-8', datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(name)40s:%(lineno)-3s %(levelname)-7s - %(message)s"
    )