"""
This module contains the class TritonCommand that implements generation of
valid tritonserver cli command using Builder pattern.
"""

MODEL_CONTROL_MODE = ("none", "poll", "explicit")

class TritonCommand:
    """
    This class implements generation of valid tritonserver cli command using
    Builder pattern.
    """
    def __init__(self, model_repository: str | list[str] = "/workspace"):
         """
         Initialize the TritonCommand object.
         """
         self._command = "tritonserver"
         self.set_model_repository(model_repository)

    def build(self):
        return self.command
    
    def _append_option(self, value: str):
        self.command += f" {value}"

    def set_model_repository(self, model_repository: str | list[str]):
        match model_repository:
            case str():
                value = f"--model-repository={model_repository}"
            case list():
                value = " ".join(
                    [f"--model-repository={path}" for path in model_repository]
                )
            case _:
                raise TypeError("Unsupported")

        self._append_option(value)

    def set_model_control_mode(self, model_control_mode: str):
        if model_control_mode not in MODEL_CONTROL_MODE:
            raise ValueError(f"Invalid model control mode: {model_control_mode}, allowed: {MODEL_CONTROL_MODE}")
        self._append_option(f"--model-control-mode={model_control_mode}")    
