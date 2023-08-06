import easypype.command as c
import easypype.log as log
import easypype.sink as s
from multiprocessing.pool import ThreadPool
import abc


class Pipe(c.Command):

    def __init__(self):
        self.pool = ThreadPool()
        self.commands = list()

    def parallelize(self, sink: s.Sink, command: c.Command):
        arguments = [(sink, )]
        sink.collect(self.pool.starmap(command.do, arguments)[0])

    def do(self, sink: s.Sink):
        for command in self.commands:
            logger = log.ConsoleLog.get(str(hash(command)))
            command_name = type(command).__name__
            msg = 'Executing {} command with args {}'.format(
                                                            command_name,
                                                            vars(command))
            logger.info(msg)
            self.parallelize(sink, command)


class PipeBuilder(abc.ABC):

    @abc.abstractproperty
    def build(self) -> Pipe:
        pass

    @abc.abstractmethod
    def command(self, command: c.Command):
        pass


class PipeBuilderConcrete(PipeBuilder):

    def __init__(self):
        self.pipe = Pipe()

    def build(self) -> Pipe:
        return self.pipe

    def command(self, command: c.Command):
        self.pipe.commands.append(command)
        return self
