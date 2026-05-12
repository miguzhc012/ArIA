"""
Cria todas as tabelas do sistema.

Esse arquivo roda apenas quando necessário.

Objetivo:
garantir que o banco exista
antes do assistente iniciar.
"""

from database.connection import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # ======================
    # Identity Memory
    # ======================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS identity_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        key TEXT UNIQUE NOT NULL,
        value TEXT NOT NULL,

        confidence REAL DEFAULT 1.0,

        category TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ======================
    # Relationship Memory
    # ======================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT UNIQUE NOT NULL,

        relationship_type TEXT,

        emotional_context TEXT,

        confidence REAL DEFAULT 1.0,

        last_mentioned TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ======================
    # Episodic Memory
    # ======================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS episodic_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        summary TEXT NOT NULL,

        emotion TEXT,

        importance REAL DEFAULT 0.5,

        tags TEXT,

        confidence REAL DEFAULT 1.0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

    print("Banco inicializado com sucesso.")