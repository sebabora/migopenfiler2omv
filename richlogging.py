import logging
from datetime import datetime

from rich.logging import RichHandler

# class CustomFormatter(logging.Formatter):
#     def formatTime(self, record, datefmt=None):
#         dt = datetime.fromtimestamp(record.created)
#         return dt.strftime('%H:%M:%S,%f')[:5]

logger = logging.getLogger(__name__)

# the handler determines where the logs go: stdout/file
shell_handler = RichHandler()
file_handler = logging.FileHandler("debug.log")

logger.setLevel(logging.DEBUG)
shell_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# the formatter determines what our logs will look like
fmt_shell = '%(message)s'
fmt_shell_date = '[%H:%M:%S]'
fmt_file = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'

shell_formatter = logging.Formatter(fmt_shell, fmt_shell_date, style="%")
# shell_formatter = CustomFormatter(fmt_shell)
shell_formatter.default_time_format = '%s.%03d'
file_formatter = logging.Formatter(fmt_file)

# here we hook everything together
shell_handler.setFormatter(shell_formatter)
file_handler.setFormatter(file_formatter)

logger.addHandler(shell_handler)
logger.addHandler(file_handler)

if __name__ == "__main__":
    logger.info('This is not working for me')
