import abc
from ...basic.cls.utils import daemon_thread

class Agent(object, metaclass=abc.ABCMeta):

    def __init__(self, **kwargs):
        super(Agent, self).__init__(**kwargs)

    #@abc.abstractmethod
    def configure(self, config_dict: dict):
        raise NotImplementedError()

    @daemon_thread
    def run(self):
        self.run_once()

    @abc.abstractmethod
    def run_once(self, **kwargs):
        raise NotImplementedError()