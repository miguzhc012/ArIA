"""
Sistema emocional simples.

Detecta emoção predominante
na mensagem do usuário.
"""


class EmotionAnalyzer:

    def analyze(
        self,
        text: str
    ):

        text = text.lower()

        emotions = {

            "feliz": [
                "feliz",
                "animado",
                "amei",
                "gostei",
                "top",
                "bom"
            ],

            "triste": [
                "triste",
                "mal",
                "desanimado",
                "depressivo",
                "sozinho"
            ],

            "ansioso": [
                "ansioso",
                "ansiedade",
                "preocupado",
                "medo",
                "nervoso"
            ],

            "estressado": [
                "raiva",
                "briga",
                "estressado",
                "ódio",
                "puto",
                "irritado"
            ]
        }

        scores = {}

        for emotion, words in (
            emotions.items()
        ):

            score = 0

            for word in words:

                if word in text:
                    score += 1

            scores[emotion] = score

        dominant = max(
            scores,
            key=scores.get
        )

        if scores[dominant] == 0:
            return "neutro"

        return dominant