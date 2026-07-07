from abc import ABC, abstractmethod

class IntegrationAdapter(ABC):
    """
    Base class for all third-party integrations (Headroom, ECC, Claude Templates, OpenHands, etc.)
    Ensures the Brain is never tightly coupled to a specific framework.
    """
    @abstractmethod
    def initialize(self):
        pass
