"""
Memória episódica.

Acontecimentos relevantes.

Não salva conversa inteira.

Salva:
- significado
- emoção
- importância
"""

from database.connection import get_connection


class EpisodicMemory:

    def save_event(
        self,
        summary: str,
        emotion: str = "",
        importance: float = 0.5,
        tags: str = ""
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO episodic_memory
        (
            summary,
            emotion,
            importance,
            tags
        )

        VALUES (?, ?, ?, ?)
        """, (
            summary,
            emotion,
            importance,
            tags
        ))

        conn.commit()
        conn.close()

    def get_recent_events(self, limit: int = 10):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM episodic_memory
        ORDER BY created_at DESC
        LIMIT ?
        """, (limit,))

        results = cursor.fetchall()

        conn.close()

        return results