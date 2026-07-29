import socket

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class DnsLookupInput(BaseModel):
    hostname: str = Field(description="Hostname to resolve (e.g. 'example.com')")
    record_type: str = Field(default="A", description="DNS record type: A, AAAA, MX, NS, CNAME")


@tool(args_schema=DnsLookupInput)
def dns_lookup(hostname: str, record_type: str = "A") -> str:
    """Look up DNS records for a hostname.

    Args:
        hostname: Hostname to resolve.
        record_type: DNS record type.

    Returns:
        Resolved addresses or records.
    """
    try:
        rtype = record_type.upper()
        if rtype == "A":
            result = socket.getaddrinfo(hostname, None, socket.AF_INET)
            ips = sorted({r[4][0] for r in result})
            return "\n".join(ips) if ips else "No A records found."
        elif rtype == "AAAA":
            result = socket.getaddrinfo(hostname, None, socket.AF_INET6)
            ips = sorted({r[4][0] for r in result})
            return "\n".join(ips) if ips else "No AAAA records found."
        else:
            return f"Error: record type '{record_type}' not supported. Use A or AAAA."
    except socket.gaierror as e:
        return f"Error resolving hostname: {e}"
    except Exception as e:
        return f"Error: {e}"


class PortCheckInput(BaseModel):
    hostname: str = Field(description="Hostname or IP")
    port: int = Field(ge=1, le=65535, description="Port number")
    timeout: float = Field(default=3.0, ge=0.5, le=30.0, description="Connection timeout")


@tool(args_schema=PortCheckInput)
def port_check(hostname: str, port: int, timeout: float = 3.0) -> str:
    """Check if a TCP port is open on a remote host.

    Args:
        hostname: Target hostname or IP.
        port: Port number.
        timeout: Connection timeout in seconds.

    Returns:
        Open or closed status.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((hostname, port))
        sock.close()
        if result == 0:
            return f"Port {port} is OPEN"
        return f"Port {port} is CLOSED"
    except socket.gaierror as e:
        return f"Error resolving hostname: {e}"
    except Exception as e:
        return f"Error: {e}"


class HttpStatusInput(BaseModel):
    url: str = Field(description="URL to check")
    timeout: int = Field(default=10, ge=1, le=60, description="Request timeout")


@tool(args_schema=HttpStatusInput)
def http_status(url: str, timeout: int = 10) -> str:
    """Check HTTP status code and response headers for a URL.

    Args:
        url: URL to check.
        timeout: Request timeout.

    Returns:
        Status code, reason, and headers.
    """
    try:
        import httpx
    except ImportError:
        return "Error: httpx is required. Install with: pip install crew-tools[web]"
    try:
        resp = httpx.get(url, follow_redirects=True, timeout=timeout)
        lines = [
            f"URL: {url}",
            f"Status: {resp.status_code} {resp.reason_phrase}",
            f"Content-Type: {resp.headers.get('content-type', 'N/A')}",
            f"Content-Length: {resp.headers.get('content-length', 'N/A')}",
            f"Server: {resp.headers.get('server', 'N/A')}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Error checking URL: {e}"
