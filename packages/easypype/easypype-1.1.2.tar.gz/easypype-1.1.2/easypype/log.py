import logging


class LogBuilder():
    """A LogBuilder.
    
    ...
    Attributes:
    - logger : Logger
        The Logger object to be setup.
    - handler: Handler
        The Handler object to be setup.
    ...
    Methods:
    - build()
        Returns the built Logger.
    - format(fmt : str)
        Sets the logger messages format.
    - level(level : int)
        Sets the logger level.
    - __init__(name : str, handler=StreamHandler)
        Begins the building of the Logger name."""

    def __init__(self, name: str, handler=logging.StreamHandler()):
        """Creates the logger instance with the default handler."""
        self.logger = logging.getLogger(name)
        self.handler = handler

    def build(self) -> logging.Logger:
        """Returns Logger instance."""
        self.logger.addHandler(self.handler)
        return self.logger

    def level(self, level : int):
        """Sets logger level."""
        self.logger.setLevel(level)
        return self

    def format(self, fmt='[%(levelname)s] %(asctime)s - %(message)s', date_fmt='%Y-%m-%d %H:%M:%S'):
        """Sets logger format."""
        self.handler.setFormatter(logging.Formatter(fmt, date_fmt))
        return self
