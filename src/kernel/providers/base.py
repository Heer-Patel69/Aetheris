from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseProvider(ABC):
    """Base interface for all capability providers."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the provider with configuration parameters."""
        pass
        
    @abstractmethod
    def start(self) -> bool:
        """Start the provider daemon or workspace instance."""
        pass
        
    @abstractmethod
    def stop(self) -> bool:
        """Stop the provider daemon or clear resources."""
        pass
        
    @abstractmethod
    def get_status(self) -> str:
        """Returns the status of the provider (e.g. running, stopped, error)."""
        pass


class CompressionCapability(BaseProvider, ABC):
    """Interface for text/context compression and SmartCrusher payloads."""
    
    @abstractmethod
    def compress(self, text: str) -> str:
        """Compress text logs, JSONs, or context strings, preserving code blocks."""
        pass


class TemplateCapability(BaseProvider, ABC):
    """Interface for syncing and translating code templates/slash commands."""
    
    @abstractmethod
    def sync_templates(self) -> Dict[str, Any]:
        """Synchronize templates, importing rules and templates as skills."""
        pass


class ExecutionCapability(BaseProvider, ABC):
    """Interface for executing isolated subprocess tasks and environment hooks."""
    
    @abstractmethod
    def execute(self, args: List[str], stdin_data: Optional[str] = None) -> Dict[str, Any]:
        """Execute commands or hooks asynchronously, returning output and status."""
        pass
