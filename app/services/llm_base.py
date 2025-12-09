from abc import ABC, abstractmethod

from typing import List

class LlmBackend(ABC):
    @abstractmethod
    def chat(self, message: List[dict]) -> str:
        raise NotImplementedError
    

