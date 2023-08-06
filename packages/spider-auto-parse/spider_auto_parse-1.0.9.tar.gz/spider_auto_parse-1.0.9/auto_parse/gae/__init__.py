from auto_parse.gae.settings import APP_DEBUG
# show_title
from loguru import logger

try:
    logger.level('inspect', no=100000 if APP_DEBUG else 0, color='<yellow>')
except (ValueError, TypeError):
    pass
