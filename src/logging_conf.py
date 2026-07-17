import logging
from src.config import config

logger = logging.getLogger(config.logging.name_app_logger)
logger.setLevel(config.logging.level)

formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(config.logging.level)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler('app.log')
file_handler.setLevel('INFO')

logger.addHandler(console_handler)
logger.addHandler(file_handler)