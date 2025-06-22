from abc import abstractmethod, ABC


class BaseReasoning(ABC):

    @abstractmethod
    def init_model(self):
        pass

    @abstractmethod
    def close_model(self):
        pass

    @abstractmethod
    def chat_blocking(self, messages):
        pass

    @abstractmethod
    def chat_stream(self, messages):
        pass
