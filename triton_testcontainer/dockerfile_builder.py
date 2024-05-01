from typing import Literal
import logging


logger = logging.getLogger("triton_testcontainer")


class DockerfileBuilder:
    """Build dockerfile

    References: https://docs.docker.com/reference/dockerfile/

    >>> DockerfileBuilder().from_('ubuntu:20.04').build()
    'FROM ubuntu:20.04'
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
        '# syntax=docker/dockerfile:1'
        """

        directive = f"{self.SYNTAX_PARSER_DIRECTIVE}{remote_image_reference}"
        self._dockerfile.insert(0, directive)
        return self
    
    # def escape(self, escape_char: Literal[r'\\'] | Literal[r"`"] | None) -> "DockerfileBuilder":
    #     """Insert escape directive

    #     >>> DockerfileBuilder().escape('\u005C').build()
    #     '# escape=\u005C'
        
        

    #     """
    #     if escape_char is None:
    #         return self
        
    #     if len(self._dockerfile) == 0:
    #         insert_position = 0
    #     else:
    #         insert_position = 1 if self._dockerfile[0].startswith(self.SYNTAX_PARSER_DIRECTIVE) else 0

    #     directive = f"{self.ESCAPE_DIRECTIVE}{escape_char}"
    #     self._dockerfile.insert(insert_position, directive)

    #     return self
    
    def append_user_instruction(self, user_instruction: str) -> "DockerfileBuilder":
        """Append user instuction

        >>> DockerfileBuilder().append_user_instruction(user_instruction="FROM ubuntu:20.04 AS stage").build()
        'FROM ubuntu:20.04 AS stage'

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
        'FROM --platform=aarch64 ubuntu:20.04 AS stage'

        >>> DockerfileBuilder().from_(user_directive="--platform=aarch64 ubuntu:20.04 AS stage").build()
        'FROM --platform=aarch64 ubuntu:20.04 AS stage'

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

        str_directive = f"FROM {' '.join(directive)}"

        self._dockerfile.append(str_directive)

        return self


    def healthcheck(self) -> ...: ...
    def label(self) -> ...: ...
    def maintainer(self) -> ...: ...
    def onbuild(self) -> ...: ...
    def run(self, 
            *args, 
            mount: str = "", 
            network: str = "", 
            security: str = "",  
            user_directive: str = ""
            ) -> "DockerfileBuilder": 
        """Append RUN instruction

        >>> DockerfileBuilder().run("echo", "hello world", mount="type=bind,source=/tmp,target=/tmp").build()
        'RUN --mount=type=bind,source=/tmp,target=/tmp echo hello world'

        >>> DockerfileBuilder().run("echo", "hello world", network="host").build()
        'RUN --network=host echo hello world'

        >>> DockerfileBuilder().run("echo", "hello world", security="insecure").build()
        'RUN --security=insecure echo hello world'

        >>> DockerfileBuilder().run("echo", "hello world", security="insecure", mount="type=bind,source=/tmp,target=/tmp").build()
        'RUN --mount=type=bind,source=/tmp,target=/tmp --security=insecure echo hello world'

        >>> DockerfileBuilder().run(user_directive="echo hello world").build()
        'RUN echo hello world'

        >>> DockerfileBuilder().run("cat", user_directive="echo hello world").build()
        'RUN echo hello world'

        """
        if user_directive:
            self._dockerfile.append(f"RUN {user_directive}")
            return self
        
        directive: list[str] = []

        if mount:
            directive.append(f"--mount={mount}")

        if network:
            directive.append(f"--network={network}")

        if security:
            directive.append(f"--security={security}")

        if not args:
            raise SyntaxError("args is required argument in 'RUN' instruction")
        
        directive.append(" ".join(args))

        str_directive = f"RUN {' '.join(directive)}"

        self._dockerfile.append(str_directive)

        return self

    def shell(self) -> ...: ...
    def stopsignal(self) -> ...: ...
    def user(self) -> ...: ...
    def volume(self) -> ...: ...
    def workdir(self) -> ...: ...



