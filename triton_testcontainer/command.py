"""
This module contains the class TritonCommand that implements generation of
valid tritonserver cli command using Builder pattern.
"""
from typing import Literal, TypeAlias, TypeVar
from pydantic import BaseModel, Field, ConfigDict

FlagType = TypeVar("FlagType", None, Literal[True])

class TritonCommand(BaseModel):
    """
    This class implements generation of valid tritonserver cli command using
    Builder pattern.
    """
    model_config = ConfigDict(protected_namespaces=())

    _command: str = "tritonserver"

    # Server

    id: None | str = None
    exit_timeout_secs: None | int = None

    # Logging
    log_verbose: None | int = None
    log_info:    None | bool = None
    log_warning: None | bool = None
    log_error:   None | bool = None
    # log_format:  None | str = None
    # log_file:    None | str = None

    # Model Repository
    model_store: None | list[str] = None
    model_repository: list[str] = Field(default_factory=lambda: ["/workspace"])

    exit_on_error: None | bool = None
    disable_auto_complete_config: FlagType = None
    strict_readiness: None | bool = None

    model_control_mode: Literal["none", "poll", "explicit"] = "none"

    repository_pool_secs: None | int = None

    load_model: None | Literal["*"] | str | list[str] = None

    model_load_thread_count: None | int = None
    model_load_retry_count: None | int = None
    model_namespacing: None | bool = None

    # HTTP
    # allow_http: None | Literal[True] = None

    # GRPS
    # allow_grpc: None | Literal[True] = None

    # Sagemaker

    # Vertex

    # Metrics
    allow_metrics: None | bool = None

    # Tracing

    # Backend

    # Repository Agent

    # Response Cache

    # Rate Limiter

    # Memory/Device Management


    def build(self):
        for fld, val in iter(self):
            annotation = str(type(self).model_fields[fld].annotation)
            self._append_option(fld, val, annotation)
        return self._command
    
    def _append_option(self, name: str, value: str | list[str], annotation: str):
        _name = name.replace("_", "-")

        match value:
            case bool():
                option = f"--{_name}" if "FlagType" in annotation else f"--{_name}={int(value)}"
            case str() | int():
                option = f"--{_name}={value}"
            case list():
                option = " ".join([f"--{_name}={v}" for v in value])
            case None:
                return
            case _:
                raise TypeError("Unsupported")

        self._command += f" {option}"
