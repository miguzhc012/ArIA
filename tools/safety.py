"""
Sistema de segurança
para terminal.
"""

import os
class CommandSafety:

    SAFE_COMMANDS = [

    "ls",
    "pwd",
    "cd",
    "cat",
    "echo",
    "ip",
    "ping",
    "curl",
    "wget",
    "nmap",
    "python",
    "pip",
    "git",
    "docker",
    "apt",
    "apt-cache",
    "grep",
    "systemctl",
    "journalctl",
    "flatpak",
    "snap"
]
    BLOCKED_PATTERNS = [

        "rm -rf",
        "mkfs",
        "shutdown",
        "reboot",
        "dd ",
        ":(){:|:&};:",
        "chmod -R",
        "chown -R"
    ]

    def is_safe(
        self,
        command
    ):

        cmd_lower = (
            command.lower()
        )

        for blocked in (
            self.BLOCKED_PATTERNS
        ):

            if blocked in cmd_lower:
                return False
            first_word = (
        command
        .split()[0]
    )

        base_command = (
            os.path.basename(
                first_word
            )
        )

        return (
            base_command
            in
            self.SAFE_COMMANDS)




    