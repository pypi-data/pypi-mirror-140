import abc
import easypype.log as log


class Sink(abc.ABC):

    @abc.abstractproperty
    def data(self):
        pass

    @abc.abstractmethod
    def collect(self, data):
        pass


class ConcreteSink(Sink):
    """A Sink implementation. It holds the Pipe data.
    
    ...
    Properties:
    - data : object
        The data loaded in memory.
        
    Methods:
    - collect(data)
        Loads data into memory.
    - __init__()
        Creates an empty sink."""

    @property
    def data(self):
        """Returns all collected data."""
        if self._data is None:
            self.get_log(self._data).warning('Sink is empty.')
        return self._data

    def get_log(self, data):
        log_builder = log.LogBuilder(str(data))
        return log_builder.format().level(20).build()

    def collect(self, data):
        """Collects the data payload."""
        self.get_log(data).info('Sinking data from {}'.format(type(data).__name__))
        self._data = data
