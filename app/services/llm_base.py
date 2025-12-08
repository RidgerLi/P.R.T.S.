from abc import ABC, abstractmethod

class LlmBackend(ABC):
    @abstractmethod
    def chat(self, message: List[Dict]) -> str:
        raise NotImplementedError
    

