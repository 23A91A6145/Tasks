"""Server-side URL safety (SSRF guard).

Every endpoint that fetches a URL from user input (knowledge URL ingest,
website crawl, browser MCP, webhooks) must route through ``validate_public_url``
so the server can never be tricked into hitting loopback, private networks,
link-local ranges or cloud metadata endpoints.
"""

import ipaddress
import socket
from urllib.parse import urlparse


def _is_private(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_unspecified
        or ip.is_reserved
        or ip.is_multicast
    )


def validate_public_url(url: str) -> str:
    """Return ``url`` if it targets a public http(s) endpoint, else raise ValueError."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http and https URLs are allowed")
    if not parsed.hostname:
        raise ValueError("URL must include a host")

    hostname = parsed.hostname
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve host '{hostname}'") from exc

    addresses = {info[4][0] for info in infos}
    if not addresses:
        raise ValueError(f"Could not resolve host '{hostname}'")

    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            continue
        if _is_private(ip):
            raise ValueError(f"Refusing to fetch a private/loopback address: {address}")
    return url
