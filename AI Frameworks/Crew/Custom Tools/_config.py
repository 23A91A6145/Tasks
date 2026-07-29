import os
from pathlib import Path

from pydantic import BaseModel, Field


class LogConfig(BaseModel):
    level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR")
    json_output: bool = Field(default=True, alias="json", description="JSON-formatted log output")
    file: str | None = Field(default=None, description="Optional log file path")


class CacheConfig(BaseModel):
    default_ttl: float = Field(default=300, ge=1, description="Default cache TTL in seconds")
    maxsize: int = Field(default=128, ge=1, description="Max cache entries")


class RateLimitConfig(BaseModel):
    default_calls_per_second: float = Field(default=10, gt=0, description="Default rate limit")


class ServerConfig(BaseModel):
    host: str = Field(default="127.0.0.1", description="API server bind host")
    port: int = Field(default=8000, ge=1024, le=65535, description="API server port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")


class Config(BaseModel):
    log: LogConfig = Field(default_factory=LogConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)


def _merge_env(cfg: Config) -> Config:
    env_map = {
        "CREW_LOG_LEVEL": ("log", "level"),
        "CREW_LOG_JSON": ("log", "json_output"),
        "CREW_LOG_FILE": ("log", "file"),
        "CREW_CACHE_TTL": ("cache", "default_ttl"),
        "CREW_CACHE_MAXSIZE": ("cache", "maxsize"),
        "CREW_RATE_LIMIT": ("rate_limit", "default_calls_per_second"),
        "CREW_SERVER_HOST": ("server", "host"),
        "CREW_SERVER_PORT": ("server", "port"),
        "CREW_SERVER_RELOAD": ("server", "reload"),
    }
    for env_key, (section, field) in env_map.items():
        val = os.environ.get(env_key)
        if val is not None:
            current = getattr(cfg, section)
            ftype = type(getattr(current, field))
            if ftype is bool:
                setattr(current, field, val.lower() in ("1", "true", "yes"))
            else:
                setattr(current, field, ftype(val))
    return cfg


def _merge_yaml(cfg: Config, path: str) -> Config:
    try:
        import yaml
    except ImportError:
        return cfg
    p = Path(path)
    if not p.is_file():
        return cfg
    with open(p) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return cfg
    for section, values in data.items():
        if hasattr(cfg, section) and isinstance(values, dict):
            current = getattr(cfg, section)
            for field, val in values.items():
                if hasattr(current, field):
                    try:
                        setattr(current, field, val)
                    except (ValueError, TypeError):
                        pass
    return cfg


def load_config(path: str | None = None) -> Config:
    cfg = Config()
    if path:
        cfg = _merge_yaml(cfg, path)
    else:
        for candidate in ("config.yaml", "config.yml", "~/.crew-tools/config.yaml"):
            expanded = os.path.expanduser(candidate)
            if os.path.isfile(expanded):
                cfg = _merge_yaml(cfg, expanded)
                break
    cfg = _merge_env(cfg)
    return cfg
