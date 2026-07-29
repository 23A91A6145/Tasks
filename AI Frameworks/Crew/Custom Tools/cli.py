import argparse
import os
import sys

from crew_tools import TOOL_REGISTRY, __version__
from crew_tools._config import load_config
from crew_tools._logging import get_logger, setup_logging

log = get_logger("cli")


def cmd_list():
    print(f"Crew Tools Library v{__version__}")
    print(f"{'Tool Name':<30} {'Description'}")
    print("-" * 80)
    for name, func in sorted(TOOL_REGISTRY.items()):
        desc = func.description if hasattr(func, "description") else (func.__doc__ or "")
        desc = desc.strip().split("\n")[0][:60]
        print(f"  {name:<30} {desc}")


def cmd_info(tool_name: str):
    func = TOOL_REGISTRY.get(tool_name)
    if not func:
        print(f"Error: tool '{tool_name}' not found. Use 'crew-tools list' to see available tools.")
        sys.exit(1)
    desc = func.description if hasattr(func, "description") else (func.__doc__ or "")
    print(f"Tool: {tool_name}")
    print("Description:")
    print(f"  {desc.strip()}")
    if hasattr(func, "args_schema") and func.args_schema:
        schema = func.args_schema.model_json_schema()
        print(f"\nParameters ({len(schema.get('properties', {}))}):")
        for pname, pinfo in schema.get("properties", {}).items():
            req = " (required)" if pname in schema.get("required", []) else ""
            print(f"  - {pname}: {pinfo.get('type', 'any')}{req}")
            if pinfo.get("description"):
                print(f"      {pinfo['description']}")


def cmd_version():
    print(f"crew-tools v{__version__}")


def cmd_config(config_path: str | None):
    cfg = load_config(config_path)
    print(cfg.model_dump_json(indent=2))


def cmd_plugins():
    from crew_tools._plugins import discover_plugins
    plugins = discover_plugins()
    if not plugins:
        print("No plugins found.")
        return
    print(f"Found {len(plugins)} plugin(s):")
    for p in plugins:
        name = p.name or type(p).__name__
        desc = p.description or ""
        print(f"  - {name}: {desc}")
        for tname in p.tools:
            print(f"      tool: {tname}")


def cmd_streamlit():
    """Launch the Streamlit UI."""
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "streamlit_app.py")
    print("Starting Streamlit UI at http://localhost:8501")
    os.execvp(sys.executable, [sys.executable, "-m", "streamlit", "run", ui_path])


def cmd_serve(args_remainder: list[str]):
    cfg = load_config()
    host = os.environ.get("CREW_SERVER_HOST") or cfg.server.host
    port = int(os.environ.get("CREW_SERVER_PORT") or cfg.server.port)
    if args_remainder:
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default=host)
        parser.add_argument("--port", type=int, default=port)
        parser.add_argument("--reload", action="store_true")
        parsed, _ = parser.parse_known_args(args_remainder)
        host = parsed.host
        port = parsed.port
        reload = parsed.reload
    else:
        reload = cfg.server.reload
    try:
        from crew_tools.api_server import serve as _serve
    except ImportError as e:
        print(f"Error: cannot start server — {e}")
        print("Install with: pip install 'crew-tools[api]'")
        sys.exit(1)
    _serve(host=host, port=port, reload=reload)


def main():
    parser = argparse.ArgumentParser(
        description="Crew Tools — LangChain-compatible AI tool library",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="list",
        choices=["list", "info", "version", "config", "plugins", "serve", "streamlit"],
        help="Command (default: list)",
    )
    parser.add_argument("tool_name", nargs="?", help="Tool name for 'info' command")
    parser.add_argument("--config", "-c", help="Path to config YAML file")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Override log level")

    args, remainder = parser.parse_known_args()

    if args.log_level:
        setup_logging(level=args.log_level)

    if args.command == "list":
        cmd_list()
    elif args.command == "info":
        if not args.tool_name:
            print("Error: tool name required. Usage: crew-tools info <tool_name>")
            sys.exit(1)
        cmd_info(args.tool_name)
    elif args.command == "version":
        cmd_version()
    elif args.command == "config":
        cmd_config(args.config)
    elif args.command == "plugins":
        cmd_plugins()
    elif args.command == "serve":
        cmd_serve(remainder)
    elif args.command == "streamlit":
        cmd_streamlit()


if __name__ == "__main__":
    main()
