import abc
import easypype.sink as s
import numbers as n


class Command(abc.ABC):

    @abc.abstractmethod
    def do(self, sink: s.Sink):
        pass


class Sum(Command):
    """A command implementation that sums some value to a iterable.
    
    ...
    Attributes:
    - amount : number
        The value to be summed.
    ...
    Methods:
    - __init__(amount : Number)
        Assigns the value to be summed."""

    def __init__(self, amount: n.Number):
        """Initializes the command with the given parameters."""
        self.amount = amount

    def sum(self, sink: s.Sink):
        return [i + self.amount for i in sink.data]

    def do(self, sink: s.Sink):
        return self.sum(sink)
