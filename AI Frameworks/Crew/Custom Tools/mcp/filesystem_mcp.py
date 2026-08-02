"""Filesystem MCP Server — Safe workspace directory and document inspection."""

import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

SENSITIVE_FILENAMES = {
    ".env",
    ".dockerenv",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "known_hosts",
    "authorized_keys",
    "kubeconfig",
}
SENSITIVE_EXTENSIONS = {".pem", ".key", ".p12", ".p8", ".pfx", ".crt", ".cer"}
SENSITIVE_PREFIXES = (".env.",)


class FilesystemMCPServer:
    """Model Context Protocol server for inspecting local files and docs safely.

    The sandbox root is the tenant upload storage directory. Paths are resolved
    and validated with ``os.path.commonpath`` (not string prefix matching) so a
    sibling directory whose name starts with the root prefix cannot escape it,
    and secrets such as ``.env`` / ``*.pem`` are always blocked.
    """

    def __init__(self, root_dir: str = "."):
        self.root_path = Path(root_dir).resolve()

    @staticmethod
    def _is_sensitive(path: Path) -> bool:
        for part in path.parts:
            if part in SENSITIVE_FILENAMES:
                return True
            if part.startswith(SENSITIVE_PREFIXES):
                return True
            if Path(part).suffix.lower() in SENSITIVE_EXTENSIONS:
                return True
        return False

    def _resolve(self, rel_path: str) -> Optional[Path]:
        """Resolve a user-supplied path inside the sandbox, or return None."""
        target = (self.root_path / rel_path).resolve()
        try:
            inside = os.path.commonpath([self.root_path, target]) == str(self.root_path)
        except ValueError:
            return None
        if not inside:
            return None
        if self._is_sensitive(target):
            return None
        return target

    def list_resources(self) -> List[Dict[str, Any]]:
        """Return available filesystem MCP resources."""
        return [
            {
                "uri": "file://workspace/storage",
                "name": "Tenant Uploads Storage",
                "mimeType": "application/octet-stream",
                "description": "Uploaded knowledge PDFs, DOCX, and text files",
            },
        ]

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return available MCP tools provided by Filesystem server."""
        return [
            {
                "name": "fs_read_file",
                "description": "Read contents of a file within the tenant upload storage.",
                "parameters": {"path": {"type": "string"}},
            },
            {
                "name": "fs_list_directory",
                "description": "List directory contents safely.",
                "parameters": {"path": {"type": "string"}},
            },
            {
                "name": "fs_search_files",
                "description": "Search for files matching a glob pattern.",
                "parameters": {"pattern": {"type": "string"}},
            },
        ]

    def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a filesystem MCP tool call."""
        if name == "fs_read_file":
            rel_path = kwargs.get("path", "")
            target = self._resolve(rel_path)
            if target is None:
                return {"error": "Access denied: Path outside the sandbox or forbidden file"}
            if not target.is_file():
                return {"error": f"File not found: {rel_path}"}
            try:
                content = target.read_text(encoding="utf-8", errors="ignore")
                return {"path": rel_path, "size": len(content), "content": content[:4000]}
            except Exception as e:  # pragma: no cover
                return {"error": str(e)}

        elif name == "fs_list_directory":
            rel_path = kwargs.get("path", ".")
            target = self._resolve(rel_path)
            if target is None:
                return {"error": "Access denied: Path outside the sandbox or forbidden file"}
            if not target.is_dir():
                return {"error": "Not a directory"}
            items = []
            for child in target.iterdir():
                if self._is_sensitive(child):
                    continue
                try:
                    items.append({
                        "name": child.name,
                        "is_dir": child.is_dir(),
                        "size": child.stat().st_size if child.is_file() else 0,
                    })
                except OSError:  # pragma: no cover
                    continue
            return {"path": rel_path, "items": items[:50]}

        elif name == "fs_search_files":
            pattern = kwargs.get("pattern", "*")
            matches = []
            for p in self.root_path.rglob("*"):
                if not p.is_file() or self._is_sensitive(p):
                    continue
                if fnmatch.fnmatch(p.name, pattern):
                    try:
                        rel = str(p.relative_to(self.root_path))
                    except ValueError:  # pragma: no cover
                        continue
                    matches.append(rel)
                    if len(matches) >= 20:
                        break
            return {"pattern": pattern, "matches": matches}

        return {"error": f"Unknown tool '{name}'"}


def make_filesystem_server() -> FilesystemMCPServer:
    """Build the filesystem server rooted at the tenant upload storage directory."""
    from ..core.config import settings

    return FilesystemMCPServer(root_dir=settings.STORAGE_DIR)
