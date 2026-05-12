"""
Resume conversa
em memória útil.
"""


class ConversationSummarizer:

    def summarize(
        self,
        user_message,
        ai_response
    ):

        text = (
            user_message.lower()
        )

        if any(
            word in text
            for word in [

                "namorada",
                "namoro",
                "briga",
                "amor"
            ]
        ):

            return (
                "Usuário discutiu "
                "assuntos de "
                "relacionamento"
            )

        if any(
            word in text
            for word in [

                "linux",
                "python",
                "erro",
                "programação"
            ]
        ):

            return (
                "Usuário discutiu "
                "tema técnico"
            )

        return None