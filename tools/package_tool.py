"""
Ferramentas para
pacotes Linux.
"""

import re

from tools.base import (
    BaseTool
)

from tools.terminal_tool import (
    TerminalTool
)


class PackageTool(
    BaseTool
):

    name = "package"

    description = (
        "Gerencia pacotes apt"
    )

    def __init__(self):

        self.terminal = (
            TerminalTool()
        )
        self.aliases = {

    "vscode": "^code$",

    "vs code": "^code$",

    "visual studio code":
        "^code$",

    "chrome":
        "google-chrome",

    "google chrome":
        "google-chrome",

    "editor de video":
        "kdenlive",

    "editor de imagem":
        "gimp",

    "gravador de tela":
        "obs",

    "obs":
        "obs",

    "python":
        "python3",

    "mysql":
        "mysql-server",

    "steam":
        "steam-installer",

    "discord":
        "discord",

    "telegram":
        "telegram-desktop",

    "spotify":
        "spotify-client"
}

    def execute(
        self,
        command: str
    ):
        pass

    def search_package(
    self,
    package_name
):
        original_name = (
    package_name
)

        print(
            "ANTES:",
            package_name
        )

        package_name = (
            package_name
            .lower()
            .strip()
        )

        if (
            package_name
            in self.aliases
        ):

            package_name = (
                self.aliases[
                    package_name
                ]
            )

        print(
            "DEPOIS:",
            package_name
        )

        search = (
            self.terminal.execute(

                f"apt-cache pkgnames "
                f"| grep '{package_name}'"
            )
        )

        # fallback inteligente
        if not search.strip():

            FALLBACKS = {

                "vscode": (
                    "VS Code não está "
                    "no repositório APT.\n"
                    "Tente instalar "
                    "via .deb oficial "
                    "ou use codium."
                ),

                "chrome": (
                    "Google Chrome "
                    "não está no APT.\n"
                    "Use o .deb oficial."
                ),

                "spotify": (
                    "Spotify normalmente "
                    "usa repositório próprio."
                )
            }

            return FALLBACKS.get(

                original_name,

                ""
            )

        return search
    

    import re


    def extract_best_match(
    self,
    search_results,
    query
):

        packages = (

            search_results
            .splitlines()
        )

        scored = []

        for pkg in packages:

            score = 0

            # MATCH EXATO = ganha absurdamente
            if pkg == query:
                score += 10000

            # começa exatamente
            elif pkg.startswith(query):
                score += 1000

            # contém query
            elif query in pkg:
                score += 200

            # penaliza nomes enormes
            difference = abs(
                len(pkg)
                - len(query)
            )

            score -= (
                difference * 10
            )

            # penaliza plugin/dev/lib
            bad_words = [

                "plugin",
                "dev",
                "dbg",
                "locale",
                "doc",
                "common"
            ]

            for word in bad_words:

                if word in pkg:
                    score -= 500

            scored.append(
                (score, pkg)
            )

        scored.sort(
            reverse=True
        )

        print(
            "\nTOP 10:"
        )

        for score, pkg in scored[:10]:

            print(
                score,
                pkg
            )

        return (
            scored[0][1]
            if scored
            else None
        )

    def install_package(
        self,
        package_name
    ):

        search = (
            self.search_package(
                package_name
            )
        )

        package = (
            self.extract_best_match(
                search
            )
        )

        if not package:

            return (
                "Nenhum pacote "
                "encontrado."
            )

        return self.terminal.execute(

            f"sudo apt install "
            f"{package} -y"
        )