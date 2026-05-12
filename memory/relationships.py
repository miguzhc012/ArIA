"""
Memória relacional.

Pessoas importantes:
- namorada
- amigos
- família
- clientes
"""

from database.connection import get_connection


class RelationshipMemory:

    def save_person(
        self,
        name,
        relationship_type,
        emotional_context=""
    ):

        existing = self.conn.execute(
            """
            SELECT id,
                relationship_type
            FROM relationships
            WHERE name = ?
            """,
            (name,)
        ).fetchone()

        if existing:

            if (
                existing[
                    "relationship_type"
                ]
                ==
                relationship_type
            ):
                return

            self.conn.execute(
                """
                UPDATE relationships
                SET relationship_type = ?,
                    emotional_context = ?,
                    confidence = 1.0,
                    updated_at =
                    CURRENT_TIMESTAMP
                WHERE name = ?
                """,
                (
                    relationship_type,
                    emotional_context,
                    name
                )
            )

        else:

            self.conn.execute(
                """
                INSERT INTO
                relationships
                (
                    name,
                    relationship_type,
                    emotional_context,
                    confidence
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    relationship_type,
                    emotional_context,
                    1.0
                )
            )

        self.conn.commit()

    def get_person(self, name: str):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM relationships
        WHERE name = ?
        """, (name,))

        result = cursor.fetchone()

        conn.close()

        return result

    def get_all_people(self):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM relationships
        """)

        results = cursor.fetchall()

        conn.close()

        return results