import abc
import logging


class Log(abc.ABC):

    @abc.abstractclassmethod
    def get(self, name: str, format=str()):
        pass


class ConsoleLog(Log):

    @classmethod
    def get(cls, name: str, fmt='[%(levelname)s] %(asctime)s - %(message)s'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        return logger
