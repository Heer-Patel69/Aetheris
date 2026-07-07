from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AetherisEngine(ABC):
    """Base Interface for all 18 Aetheris Engines"""
    @abstractmethod
    def initialize(self, event_bus: 'EventBus') -> None:
        pass
        
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        pass

class IntegrationAdapter(ABC):
    """Base Interface for Integration Plugins (Headroom, ECC, OpenHands)"""
    @abstractmethod
    def load(self, config: Dict[str, Any]) -> bool:
        pass
        
    @abstractmethod
    def execute_capability(self, capability: str, context: Dict[str, Any]) -> Any:
        pass
