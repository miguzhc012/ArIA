"""
Gerencia a conexão com SQLite.

Por que existe?

Não queremos abrir conexão direto em vários arquivos.

Se amanhã trocar SQLite por PostgreSQL,
mudamos apenas aqui.
"""

from pathlib import Path
import sqlite3

# Caminho absoluto do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Pasta database/
DB_FOLDER = BASE_DIR / "database"

# Garante que existe
DB_FOLDER.mkdir(exist_ok=True)

# Arquivo do banco
DB_PATH = DB_FOLDER / "memory.db"


def get_connection() -> sqlite3.Connection:
    """
    Retorna conexão SQLite configurada.

    Row factory permite acessar:
    row["name"]

    em vez de:
    row[0]
    """

    conn = sqlite3.connect(DB_PATH)

    # retorna dict-like rows
    conn.row_factory = sqlite3.Row

    return conn