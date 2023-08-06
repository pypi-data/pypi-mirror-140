import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from colorlog import ColoredFormatter

levels = ['调试', '信息', '警告', '错误', '严重']


class ContextFilter(logging.Filter):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def filter(self, record):
        return record.levelname in self.logger.levels_dynamic


class Logger:
    def __init__(self, file: str, formatter: str = '%(asctime)s %(levelname)s: %(message)s', save: int = 2):
        self.factory = logging.getLogger()
        self.filter = ContextFilter(self)
        self.file = file
        self.save = save
        self.formatter = formatter
        self.levels_dynamic = levels[1:]
        self.__init()

    def __init(self):
        logging.addLevelName(logging.DEBUG, levels[0])
        logging.addLevelName(logging.INFO, levels[1])
        logging.addLevelName(logging.WARNING, levels[2])
        logging.addLevelName(logging.ERROR, levels[3])
        logging.addLevelName(logging.CRITICAL, levels[4])
        self.factory.setLevel(logging.DEBUG)
        self.__set_console_handler()
        self.__set_file_handler()

    def __set_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter(f'%(log_color)s{self.formatter}', log_colors={
            levels[0]: 'cyan',
            levels[1]: 'green',
            levels[2]: 'yellow',
            levels[3]: 'red',
            levels[4]: 'purple'}))
        console_handler.addFilter(self.filter)
        self.factory.addHandler(console_handler)

    def __set_file_handler(self):
        path = os.path.dirname(self.file)
        if path:
            os.makedirs(path, exist_ok=True)
        if self.save == 1:
            file_handler = TimedRotatingFileHandler(self.file, encoding='utf-8', when='midnight', backupCount=7)
        elif self.save == 2:
            file_handler = RotatingFileHandler(self.file, encoding='utf-8', maxBytes=1024 * 1024 * 10, backupCount=10)
        else:
            file_handler = logging.FileHandler(self.file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(self.formatter))
        file_handler.addFilter(self.filter)
        self.factory.addHandler(file_handler)

    def debug(self, message: str):
        self.factory.debug(message)

    def info(self, message: str):
        self.factory.info(message)

    def warning(self, message: str):
        self.factory.warning(message)

    def error(self, message: str):
        self.factory.error(message)

    def critical(self, message: str):
        self.factory.critical(message)
