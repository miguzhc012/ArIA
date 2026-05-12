"""
Memória de identidade.

Coisas estáveis do usuário:
- nome
- idade
- sistema operacional
- gostos
- objetivos

Ex:
"uso Linux"
"meu nome é Miguel"
"""

from database.connection import get_connection


class IdentityMemory:

    def save(
        self,
        key,
        value,
        category="general"
    ):

        existing = self.conn.execute(
            """
            SELECT id, value
            FROM identity_memory
            WHERE key = ?
            """,
            (key,)
        ).fetchone()

        if existing:

            if existing["value"] == value:
                return

            self.conn.execute(
                """
                UPDATE identity_memory
                SET value = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    confidence = 1.0
                WHERE key = ?
                """,
                (value, key)
            )

        else:

            self.conn.execute(
                """
                INSERT INTO identity_memory
                (
                    key,
                    value,
                    category,
                    confidence
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    key,
                    value,
                    category,
                    1.0
                )
            )

        self.conn.commit()

    def get(self, key: str):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM identity_memory
        WHERE key = ?
        """, (key,))

        result = cursor.fetchone()

        conn.close()

        return result

    def get_all(self):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM identity_memory
        """)

        results = cursor.fetchall()

        conn.close()

        return results