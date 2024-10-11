from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Abstract base class for all publishing strategies.
    """

    @abstractmethod
    def execute(self) -> None:
        """
        Executes the strategy.
        """
        pass
