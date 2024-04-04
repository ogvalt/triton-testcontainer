"""
This module contains the class TritonCommand that implements generation of
valid tritonserver cli command using Builder pattern.
"""
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class TritonCommand(BaseModel):
    """
    This class implements generation of valid tritonserver cli command using
    Builder pattern.
    """
    model_config = ConfigDict(protected_namespaces=())

    _command: str = "tritonserver"

    # Logging
    log_verbose: None | int = None
    log_info:    None | Literal[0, 1] = None
    log_warning: None | Literal[0, 1] = None
    log_error:   None | Literal[0, 1] = None
    log_format:  None | str = None
    log_file:    None | str = None

    # Model Repository
    model_store: None | list[str] = None
    model_repository: list[str] = Field(default_factory=lambda: ["/workspace"])

    exit_on_error: None | Literal[0, 1] = None
    # disable_auto_complete_config: None | Literal[True] = None
    strict_readiness: None | Literal[0, 1] = None
    model_control_mode: Literal["none", "poll", "explicit"] = "none"

    repository_pool_secs: None | int = None

    load_model: None | Literal["*"] | str | list[str] = None
    model_load_retry_count: None | int = None
    # model_namespacing: None | Literal[True] = None

    # HTTP
    # allow_http: None | Literal[True] = None

    # GRPS
    # allow_grpc: None | Literal[True] = None

    def build(self):
        for fld, val in iter(self):
            self._append_option(fld, val)
        return self._command
    
    def _append_option(self, name: str, value: str | list[str]):
        _name = name.replace("_", "-")

        match value:
            case str():
                option = f"--{_name}={value}"
            case list():
                option = " ".join([f"--{_name}={v}" for v in value])
            case None:
                return
            case _:
                raise TypeError("Unsupported")

        self._command += f" {option}"


if __name__ == "__main__":
    cmd = TritonCommand(
        model_repository=["/workspace", "/home"], 
        model_control_mode="explicit", 
        load_model=["simple", "hard"],
    )
    print(cmd.build())