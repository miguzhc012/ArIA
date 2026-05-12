"""
Sistema de esquecimento inteligente.

Memórias perdem confiança
com o tempo.

Objetivo:
não assumir coisas antigas.
"""

from datetime import datetime


class MemoryDecay:

    def calculate_confidence(
        self,
        original_confidence: float,
        days_since_update: int,
        memory_type: str
    ) -> float:

        decay_rates = {

            # quase permanente
            "identity": 0.001,

            # média estabilidade
            "relationship": 0.005,

            # muda rápido
            "episodic": 0.02
        }

        decay = decay_rates.get(
            memory_type,
            0.01
        )

        new_confidence = (
            original_confidence
            - (days_since_update * decay)
        )

        return max(new_confidence, 0.1)

    def should_confirm(
        self,
        confidence: float
    ) -> bool:

        return confidence < 0.60

    def days_since(
        self,
        timestamp: str
    ) -> int:

        last_date = datetime.fromisoformat(
            timestamp
        )

        now = datetime.now()

        difference = now - last_date

        return difference.days