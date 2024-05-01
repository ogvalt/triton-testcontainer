from typing import Literal
import logging


logger = logging.getLogger("triton_testcontainer")


class DockerfileBuilder:
    """Build dockerfile

    References: https://docs.docker.com/reference/dockerfile/

    >>> DockerfileBuilder().from('ubuntu:20.04').build()
    FROM ubuntu:20.04
    """

    SYNTAX_PARSER_DIRECTIVE = "# syntax="
    ESCAPE_DIRECTIVE = "# escape="

    def __init__(self) -> None:
        self._dockerfile: list[str] = []
    
    def build(self) -> str: 
        return """{}""".format("\n".join(self._dockerfile))

    def syntax(self, remote_image_reference: str = "docker/dockerfile:1") -> "DockerfileBuilder": 
        """Insert syntax directive

        >>> DockerfileBuilder().syntax().build()
        # syntax=docker/dockerfile:1
        """

        directive = f"{self.SYNTAX_PARSER_DIRECTIVE}{remote_image_reference}"
        self._dockerfile.insert(0, remote_image_reference)
        return self
    
    def escape(self, escape_char: Literal["\\"] | Literal["`"] | None) -> "DockerfileBuilder":
        """Insert escape directive

        >>> DockerfileBuilder().escape("\\").build()
        # escape=\
        >>> DockerfileBuilder().escape("`").build()
        # escape=`
        >>> DockerfileBuilder().syntax().escape("\\").build()
        # syntax=docker/dockerfile:1\n# escape=\

        """
        if escape_char is None:
            return self
        
        insert_position = 1 if self._dockerfile[0].startswith(self.SYNTAX_PARSER_DIRECTIVE) else 0

        directive = f"{self.ESCAPE_DIRECTIVE}{escape_char}"
        self._dockerfile.insert(insert_position, directive)

        return self
    
    def append_user_instruction(self, user_instruction: str) -> "DockerfileBuilder":
        """Append user instuction

        >>> DockerfileBuilder().append_user_instruction(user_instruction="FROM ubuntu:20.04 AS stage").build()
        FROM ubuntu:20.04 AS stage

        """
        
        self._dockerfile.append(user_instruction)

        return self
    
    def add(self) -> ...: ...
    def arg(self) -> ...: ...
    def cmd(self) -> ...: ...
    def copy(self) -> ...: ...
    def entrypoint(self) -> ...: ...
    def env(self) -> ...: ...
    def expose(self) -> ...: ...
    def add(self) -> ...: ...

    def from_(self, image: str = "ubuntu:20.04", 
              platform: str = "", 
              as_name: str = "", 
              user_directive: str = ""
              ) -> "DockerfileBuilder": 
        """Append FROM instruction

        >>> DockerfileBuilder().from_(image="ubuntu:20.04", platform="aarch64", as_name="stage").build()
        FROM --platform=aarch64 ubuntu:20.04 AS stage

        >>> DockerfileBuilder().from_(user_directive="--platform=aarch64 ubuntu:20.04 AS stage").build()
        FROM --platform=aarch64 ubuntu:20.04 AS stage

        """

        if user_directive:
            self._dockerfile.append(f"FROM {user_directive}")
            return self
        
        directive: list[str] = []

        if platform:
            directive.append(f"--platform={platform}")

        if not image:
            raise SyntaxError("image is required argument in 'FROM' instruction")
        
        directive.append(image)

        if as_name:
            directive.append(f"AS {as_name}")

        str_directive = f"FROM {" ".join(directive)}"

        self._dockerfile.append(str_directive)

        return self


    def healthcheck(self) -> ...: ...
    def label(self) -> ...: ...
    def maintainer(self) -> ...: ...
    def onbuild(self) -> ...: ...
    def run(self) -> ...: ...
    def shell(self) -> ...: ...
    def stopsignal(self) -> ...: ...
    def user(self) -> ...: ...
    def volume(self) -> ...: ...
    def workdir(self) -> ...: ...



