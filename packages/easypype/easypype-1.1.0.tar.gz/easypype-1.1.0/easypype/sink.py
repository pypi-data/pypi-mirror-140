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

    @property
    def data(self):
        return self._data

    def collect(self, data):
        logger = log.ConsoleLog.get(str(data))
        logger.info('Sinking data of {}'.format(type(data).__name__))
        self._data = data
