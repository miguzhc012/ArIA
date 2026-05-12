"""
Extrator simples de memória.

Detecta informações importantes
nas mensagens do usuário.
"""

import re


class MemoryExtractor:

    def extract(self, text: str):

        text_lower = text.lower()

        extracted = {
            "identity": [],
            "relationships": [],
            "events": []
        }

        # ======================
        # IDENTIDADE
        # ======================

        identity_patterns = {

            "nome": [
                r"meu nome é (.+)"
            ],

            "idade": [
                r"tenho (\d+) anos"
            ],

            "sistema": [
                r"uso (linux|windows|ubuntu|zorin|opensuse)"
            ]
        }

        for key, patterns in identity_patterns.items():

            for pattern in patterns:

                match = re.search(
                    pattern,
                    text_lower
                )

                if match:

                    value = (
                        match.group(1)
                        .strip()
                    )

                    extracted[
                        "identity"
                    ].append({
                        "key": key,
                        "value": value
                    })

        # ======================
        # RELACIONAMENTOS
        # ======================

        relationship_patterns = [

            (
                r"minha namorada é (.+)",
                "namorada"
            ),

            (
                r"meu namorado é (.+)",
                "namorado"
            )
        ]

        for pattern, relation in relationship_patterns:

            match = re.search(
                pattern,
                text_lower
            )

            if match:

                person_name = (
                    match.group(1)
                    .strip()
                    .title()
                )

                extracted[
                    "relationships"
                ].append({

                    "name": person_name,

                    "relationship_type":
                    relation,

                    "emotional_context":
                    ""
                })

        # ======================
        # EVENTOS
        # ======================

        emotional_keywords = {

            "triste":
            "triste",

            "feliz":
            "feliz",

            "ansioso":
            "ansioso",

            "briga":
            "estressado",

            "discussão":
            "estressado",

            "inseguro":
            "inseguro"
        }

        detected_emotion = ""

        for keyword, emotion in (
            emotional_keywords.items()
        ):

            if keyword in text_lower:

                detected_emotion = emotion

                extracted[
                    "events"
                ].append({

                    "summary":
                    text,

                    "emotion":
                    emotion,

                    "importance":
                    0.7,

                    "tags":
                    "emocional"
                })

                break

        return extracted