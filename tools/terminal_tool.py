"""
Executa comandos
do terminal.
"""

import subprocess
import shutil

from tools.base import (
    BaseTool
)

from tools.safety import (
    CommandSafety
)


class TerminalTool(
    BaseTool
):

    name = "terminal"

    description = (
        "Executa comandos Linux"
    )

    def __init__(self):

        self.safety = (
            CommandSafety()
        )

    def execute(
        self,
        command: str
    ):
        import os

        safe_env = os.environ.copy()

        safe_env["PATH"] = (
            "/usr/local/sbin:"
            "/usr/local/bin:"
            "/usr/sbin:"
            "/usr/bin:"
            "/sbin:"
            "/bin:"
            + safe_env.get(
                "PATH",
                ""
            )
        )

        if not self.safety.is_safe(
            command
        ):

            return (
                "Comando bloqueado "
                "por segurança."
            )

        try:

            parts = (
                command.split()
            )

            binary = shutil.which(
    parts[0],
    path=safe_env["PATH"]
)

            if not binary:

                return (
                    f"Comando "
                    f"'{parts[0]}' "
                    f"não encontrado."
                )

            parts[0] = binary

            result = subprocess.run(

    command,

    shell=True,

    executable="/bin/bash",

    capture_output=True,

    text=True,

    timeout=30
)

            if result.stdout:
                return result.stdout

            return result.stderr

        except Exception as e:

            return str(e)