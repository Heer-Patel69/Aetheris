import importlib
from typing import Dict, Any, Type
from kernel.providers.base import BaseProvider

class CapabilityRegistry:
    """
    Central Capability Registry implementing Dependency Injection.
    Maps abstract capability tags to decoupled provider implementations.
    The Aetheris Kernel never references concrete provider classes directly.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CapabilityRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, workspace_path: str = "."):
        if self._initialized:
            return
        self.workspace_path = workspace_path
        self._registry: Dict[str, BaseProvider] = {}
        self._provider_classes: Dict[str, Dict[str, str]] = {
            "compression": {
                "module": "kernel.providers.headroom_provider",
                "class": "HeadroomProvider"
            },
            "templates": {
                "module": "kernel.providers.claude_template_provider",
                "class": "ClaudeTemplateProvider"
            },
            "hooks": {
                "module": "kernel.providers.ecc_provider",
                "class": "ECCProvider"
            }
        }
        self._initialized = True

    def register(self, capability: str, provider: BaseProvider) -> None:
        """Manually register a concrete provider for a capability."""
        self._registry[capability] = provider

    def resolve(self, capability: str) -> BaseProvider:
        """
        Resolves and returns the concrete provider for a capability.
        Dynamically imports and lazy-loads the provider on demand.
        """
        if capability in self._registry:
            return self._registry[capability]
            
        if capability in self._provider_classes:
            info = self._provider_classes[capability]
            try:
                module = importlib.import_module(info["module"])
                provider_class: Type[BaseProvider] = getattr(module, info["class"])
                # Instantiate the provider passing the workspace root
                provider_instance = provider_class(self.workspace_path)
                # Initialize it with empty config by default
                provider_instance.initialize({})
                self._registry[capability] = provider_instance
                return provider_instance
            except Exception as e:
                raise ImportError(f"Failed to dynamically load provider for capability '{capability}': {e}")
                
        raise KeyError(f"Capability '{capability}' is not registered in the Capability Registry.")

    def clear(self) -> None:
        """Clear all active providers, stopping daemon instances if running."""
        for provider in self._registry.values():
            try:
                provider.stop()
            except Exception:
                pass
        self._registry.clear()
