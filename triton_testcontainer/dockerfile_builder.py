import logging

logger = logging.getLogger("triton_testcontainer")


class DockerfileBuilder:
    """Build dockerfile

    References: https://docs.docker.com/reference/dockerfile/

    >>> print(DockerfileBuilder() \
    .syntax() \
    .arg(name="BASE_IMAGE") \
    .from_('${BASE_IMAGE}', as_name="stage") \
    .env(key="DEBIAN_FRONTEND", value="noninteractive") \
    .run("apt-get update && apt-get install curl") \
    .label("maintaner", "oleksandr") \
    .cmd("curl", "localhost") \
    .build())
    # syntax=docker/dockerfile:1
    ARG BASE_IMAGE
    FROM ${BASE_IMAGE} AS stage
    ENV DEBIAN_FRONTEND=noninteractive
    RUN apt-get update && apt-get install curl
    LABEL maintaner=oleksandr
    CMD curl localhost

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

    def add(self,
            src: str = "",
            dest: str = "",
            keep_git_dir: bool = False,
            checksum: str = "",
            chown: str = "",
            chmod: str = "",
            link: bool = False,
            exclude: list[str] = None,
            user_directive: str = "",
            ) -> "DockerfileBuilder":
        """Append ADD instruction

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt").build()
        'ADD file.txt /file.txt'

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt", keep_git_dir=True).build()
        'ADD --keep-git-dir=true file.txt /file.txt'

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt", checksum="sha256:123").build()
        'ADD --checksum=sha256:123 file.txt /file.txt'

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt", chown="user:group").build()
        'ADD --chown=user:group file.txt /file.txt'

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt", chmod="777").build()
        'ADD --chmod=777 file.txt /file.txt'

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt", link=True).build()
        'ADD --link file.txt /file.txt'

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt", exclude=["file.txt"]).build()
        'ADD --exclude=file.txt file.txt /file.txt'

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt", exclude=["file.txt", ".git"]).build()
        'ADD --exclude=file.txt --exclude=.git file.txt /file.txt'

        >>> DockerfileBuilder().add(user_directive="--chown=user:group --chmod=644 files* /somedir/").build()
        'ADD --chown=user:group --chmod=644 files* /somedir/'

        >>> DockerfileBuilder().add(src="file.txt", dest="/file.txt", keep_git_dir=True, \
            checksum="sha256:123", chown="user:group", chmod="777", link=True, exclude=["file.txt"]).build()
        'ADD --keep-git-dir=true --checksum=sha256:123 --chown=user:group --chmod=777 --link --exclude=file.txt file.txt /file.txt'
        """

        if user_directive:
            self._dockerfile.append(f"ADD {user_directive}")
            return self

        if not src or not dest:
            raise SyntaxError("ADD: you must either specify (src, dest) or (user_directive)")

        if exclude is None:
            exclude = []

        directive = []

        if keep_git_dir:
            directive.append("--keep-git-dir=true")

        if checksum:
            directive.append(f"--checksum={checksum}")

        if chown:
            directive.append(f"--chown={chown}")

        if chmod:
            directive.append(f"--chmod={chmod}")

        if link:
            directive.append("--link")

        if exclude:
            for item in exclude:
                directive.append(f"--exclude={item}")

        directive.extend([src, dest])

        str_directive = f"ADD {' '.join(directive)}"

        self._dockerfile.append(str_directive)
        return self

    def arg(self, name: str, default: str = "") -> "DockerfileBuilder":
        """Append ARG instruction

        >>> DockerfileBuilder().arg(name="VAR").build()
        'ARG VAR'

        >>> DockerfileBuilder().arg(name="VAR", default="value").build()
        'ARG VAR=value'

        """
        if default:
            self._dockerfile.append(f"ARG {name}={default}")
        else:
            self._dockerfile.append(f"ARG {name}")

        return self

    def cmd(self, executable: str = "", *params) -> "DockerfileBuilder":
        """Append CMD instruction

        >>> DockerfileBuilder().cmd("echo", "hello world").build()
        'CMD echo hello world'

        """
        directive = []
        if executable:
            directive.append(executable)

        directive.extend(params)

        str_directive = f"CMD {' '.join(directive)}"

        self._dockerfile.append(str_directive)

        return self

    def copy(self,
             src: str = "",
             dest: str = "",
             from_: str = "",
             chown: str = "",
             chmod: str = "",
             link: bool = False,
             parents: bool = False,
             exclude: list[str] = None,
             user_directive: str = "",
             ) -> "DockerfileBuilder":
        """Append COPY instruction

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt").build()
        'COPY file.txt /file.txt'

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt", from_="stage").build()
        'COPY --from=stage file.txt /file.txt'

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt", parents=True).build()
        'COPY --parents file.txt /file.txt'

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt", chown="user:group").build()
        'COPY --chown=user:group file.txt /file.txt'

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt", chmod="777").build()
        'COPY --chmod=777 file.txt /file.txt'

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt", link=True).build()
        'COPY --link file.txt /file.txt'

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt", exclude=["file.txt"]).build()
        'COPY --exclude=file.txt file.txt /file.txt'

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt", exclude=["file.txt", ".git"]).build()
        'COPY --exclude=file.txt --exclude=.git file.txt /file.txt'

        >>> DockerfileBuilder().copy(user_directive="--chown=user:group --chmod=644 files* /somedir/").build()
        'COPY --chown=user:group --chmod=644 files* /somedir/'

        >>> DockerfileBuilder().copy(src="file.txt", dest="/file.txt", from_="stage", \
            chown="user:group", chmod="777", link=True, parents=True, exclude=["file.txt"]).build()
        'COPY --from=stage --chown=user:group --chmod=777 --link --parents --exclude=file.txt file.txt /file.txt'
        """

        if user_directive:
            self._dockerfile.append(f"COPY {user_directive}")
            return self

        if not src or not dest:
            raise SyntaxError("ADD: you must either specify (src, dest) or (user_directive)")

        if exclude is None:
            exclude = []

        directive = []

        if from_:
            directive.append(f"--from={from_}")

        if chown:
            directive.append(f"--chown={chown}")

        if chmod:
            directive.append(f"--chmod={chmod}")

        if link:
            directive.append("--link")

        if parents:
            directive.append("--parents")

        if exclude:
            for item in exclude:
                directive.append(f"--exclude={item}")

        directive.extend([src, dest])

        str_directive = f"COPY {' '.join(directive)}"

        self._dockerfile.append(str_directive)
        return self

    def entrypoint(self, executable: str = "", *params) -> "DockerfileBuilder":
        """Append ENTRYPOINT instruction

        >>> DockerfileBuilder().entrypoint("echo", "hello world").build()
        'ENTRYPOINT echo hello world'

        """
        directive = []
        if executable:
            directive.append(executable)

        directive.extend(params)

        str_directive = f"ENTRYPOINT {' '.join(directive)}"

        self._dockerfile.append(str_directive)

        return self

    def env(self, key: str = "", value: str = "", user_directive: str = "") -> "DockerfileBuilder":
        """Append ENV instruction

        >>> DockerfileBuilder().env(key="key", value="value").build()
        'ENV key=value'

        >>> DockerfileBuilder().env(user_directive="key1=value1 key2=value2").build()
        'ENV key1=value1 key2=value2'

        """
        if user_directive:
            self._dockerfile.append(f"ENV {user_directive}")
            return self

        if not key or not value:
            raise SyntaxError("ENV: you must either specify (key, value) or (user_directive)")

        str_directive = f"ENV {key}={value}"

        self._dockerfile.append(str_directive)
        return self

    def expose(self, port: int | str, protocol: str = "") -> "DockerfileBuilder":
        """Append EXPOSE instruction

        >>> DockerfileBuilder().expose(port=80).build()
        'EXPOSE 80'

        >>> DockerfileBuilder().expose(port=80, protocol="tcp").build()
        'EXPOSE 80/tcp'

        """
        directive = [str(port)]

        if protocol:
            directive.append(protocol)

        str_directive = f"EXPOSE {'/'.join(directive)}"

        self._dockerfile.append(str_directive)

        return self

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

    def healthcheck(self,
                    disable: bool = False,
                    command: str = "",
                    interval: str = "30s",
                    timeout: str = "30s",
                    start_period: str = "0s",
                    retries: int | None = 3,
                    user_directive: str = ""
                    ) -> "DockerfileBuilder":
        """Append HEALTHCHECK instruction

        >>> DockerfileBuilder().healthcheck(disable=True).build()
        'HEALTHCHECK NONE'

        >>> DockerfileBuilder().healthcheck(command="CMD curl -f http://localhost/ || exit 1", interval="60s", timeout="70s", start_period="80s", retries=3).build()
        'HEALTHCHECK --interval=60s --timeout=70s --start-period=80s --retries=3 CMD curl -f http://localhost/ || exit 1'

        >>> DockerfileBuilder().healthcheck(user_directive="--interval=5m --timeout=3s CMD curl -f http://localhost/ || exit 1").build()
        'HEALTHCHECK --interval=5m --timeout=3s CMD curl -f http://localhost/ || exit 1'

        """
        if user_directive:
            self._dockerfile.append(f"HEALTHCHECK {user_directive}")
            return self

        if disable:
            self._dockerfile.append("HEALTHCHECK NONE")
            return self

        directive = []

        if interval:
            directive.append(f"--interval={interval}")

        if timeout:
            directive.append(f"--timeout={timeout}")

        if start_period:
            directive.append(f"--start-period={start_period}")

        if retries:
            directive.append(f"--retries={retries}")

        if not command:
            raise SyntaxError("HEALTHCHECK: you should either specify (disable=True) or (command) or (user_directive)")

        directive.append(command)

        str_directive = f"HEALTHCHECK {' '.join(directive)}"
        self._dockerfile.append(str_directive)

        return self

    def label(self, key: str = "", value: str = "", user_directive: str = "") -> "DockerfileBuilder":
        """Append LABEL instruction

        >>> DockerfileBuilder().label(key="version", value="1.0.0").build()
        'LABEL version=1.0.0'

        >>> DockerfileBuilder().label(user_directive='multi.label1="value1" milti.label2="value2"').build()
        'LABEL multi.label1="value1" milti.label2="value2"'

        """
        if user_directive:
            self._dockerfile.append(f"LABEL {user_directive}")
            return self

        if not key or not value:
            raise SyntaxError("LABEL: you must either specify (key, value) or (user_directive)")

        directive = f"{key}={value}"

        self._dockerfile.append(f"LABEL {directive}")

        return self

    def maintainer(self, name: str) -> "DockerfileBuilder":
        """Append MAINTAINER instruction

        >>> DockerfileBuilder().maintainer(name="oleksandr").build()
        'MAINTAINER oleksandr'

        """
        logger.warning("maintainer is deprecated. Use LABEL instead.")

        self._dockerfile.append(f"MAINTAINER {name}")

        return self

    def onbuild(self, user_directive: str) -> "DockerfileBuilder":
        """Append ONBUILD instruction

        >>> DockerfileBuilder().onbuild("RUN /usr/local/bin/python-build --dir /app/src").build()
        'ONBUILD RUN /usr/local/bin/python-build --dir /app/src'

        """
        self._dockerfile.append(f"ONBUILD {user_directive}")

        return self

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

    def shell(self, executable: str, parameters: list[str]) -> "DockerfileBuilder":
        """Append SHELL instruction

        >>> DockerfileBuilder().shell(executable="/bin/bash", parameters=["-c"]).build()
        'SHELL ["/bin/bash", "-c"]'

        >>> DockerfileBuilder().shell(executable="cmd", parameters=["/S", "/C"]).build()
        'SHELL ["cmd", "/S", "/C"]'

        """
        directive = [executable]
        directive.extend(parameters)

        quoted_directive = [f'"{item}"' for item in directive]

        str_directive = f"SHELL {'[' + ', '.join(quoted_directive) + ']'}"

        self._dockerfile.append(str_directive)

        return self

    def stopsignal(self, signal: str) -> "DockerfileBuilder":
        """Append STOPSIGNAL instruction

        >>> DockerfileBuilder().stopsignal(signal="SIGKILL").build()
        'STOPSIGNAL SIGKILL'

        >>> DockerfileBuilder().stopsignal(signal="9").build()
        'STOPSIGNAL 9'

        """
        self._dockerfile.append(f"STOPSIGNAL {signal}")

        return self

    def user(self, user: str, group: str = "") -> "DockerfileBuilder":
        """Append USER instruction

        >>> DockerfileBuilder().user(user="root").build()
        'USER root'

        >>> DockerfileBuilder().user(user="root", group="root").build()
        'USER root:root'

        """
        if group:
            self._dockerfile.append(f"USER {user}:{group}")
        else:
            self._dockerfile.append(f"USER {user}")

        return self

    def volume(self, name: str) -> "DockerfileBuilder":
        """Append VOLUME instruction

        >>> DockerfileBuilder().volume(name="data").build()
        'VOLUME data'

        """
        self._dockerfile.append(f"VOLUME {name}")

        return self

    def workdir(self, path: str) -> "DockerfileBuilder":
        """Append WORKDIR instruction

        >>> DockerfileBuilder().workdir(path="/path/to/workdir").build()
        'WORKDIR /path/to/workdir'

        """
        self._dockerfile.append(f"WORKDIR {path}")

        return self
