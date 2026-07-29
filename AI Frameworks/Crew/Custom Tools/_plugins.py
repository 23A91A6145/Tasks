import logging
from typing import Any

log = logging.getLogger("crew_tools.plugins")


class ToolPlugin:
    name: str = ""
    description: str = ""
    tools: dict[str, Any] | None = None

    def __init__(self) -> None:
        if self.tools is None:
            self.tools = {}

    def register(self, registry: dict[str, Any]) -> None:
        registry.update(self.tools)


def discover_plugins() -> list[ToolPlugin]:
    plugins: list[ToolPlugin] = []
    try:
        from importlib.metadata import entry_points
    except ImportError:
        return plugins
    try:
        eps = entry_points(group="crew_tools.plugins")
    except TypeError:
        eps = entry_points()
        eps = eps.get("crew_tools.plugins", [])
    for ep in eps:
        try:
            cls = ep.load()
            instance = cls()
            plugins.append(instance)
            log.info("Loaded plugin: %s", ep.name)
        except Exception as e:
            log.warning("Failed to load plugin '%s': %s", ep.name, e)
    return plugins


def load_plugins(registry: dict[str, Any]) -> list[ToolPlugin]:
    plugins = discover_plugins()
    for plugin in plugins:
        try:
            plugin.register(registry)
            log.info("Registered tools from plugin: %s", plugin.name or type(plugin).__name__)
        except Exception as e:
            log.warning("Failed to register plugin '%s': %s", plugin.name, e)
    return plugins
