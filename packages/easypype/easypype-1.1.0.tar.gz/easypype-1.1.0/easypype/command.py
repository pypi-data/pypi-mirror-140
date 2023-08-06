import abc
import easypype.sink as s


class Command(abc.ABC):

    @abc.abstractmethod
    def do(self, sink: s.Sink):
        pass


class Sum(Command):

    def __init__(self, amount):
        self.amount = amount

    def sum(self, sink: s.Sink):
        return [i + self.amount for i in sink.data]

    def do(self, sink: s.Sink):
        return self.sum(sink)
