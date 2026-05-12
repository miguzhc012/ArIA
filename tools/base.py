"""
Classe base de tools.
"""

from abc import ABC, abstractmethod


class BaseTool(ABC):

    name = "base"
    description = ""

    @abstractmethod
    def execute(
        self,
        command: str
    ):
        pass