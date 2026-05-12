"""
Memory Manager

Centraliza toda a memória.

O agent.py vai conversar
apenas com ele.
"""

from memory.emotion import (EmotionAnalyzer)
from memory.summarizer import (ConversationSummarizer)
from memory.extractor import MemoryExtractor
from memory.identity import IdentityMemory
from memory.relationships import RelationshipMemory
from memory.episodic import EpisodicMemory
from memory.decay import MemoryDecay


class MemoryManager:

    def __init__(self):

        self.extractor = MemoryExtractor()

        self.identity = IdentityMemory()

        self.relationships = (
            RelationshipMemory()
        )

        self.episodic = (
            EpisodicMemory()
        )

        self.decay = MemoryDecay()

        self.summarizer = (ConversationSummarizer())

        self.emotion = (
    EmotionAnalyzer()
)
    # ======================
    # SAVE METHODS
    # ======================

    def save_identity(
        self,
        key,
        value,
        category="general"
    ):

        self.identity.save(
            key=key,
            value=value,
            category=category
        )

    def save_relationship(
        self,
        name,
        relationship_type,
        emotional_context=""
    ):

        self.relationships.save_person(
            name=name,
            relationship_type=relationship_type,
            emotional_context=emotional_context
        )

    def save_event(
        self,
        summary,
        emotion="",
        importance=0.5,
        tags=""
    ):

        self.episodic.save_event(
            summary=summary,
            emotion=emotion,
            importance=importance,
            tags=tags
        )

    # ======================
    # GET METHODS
    # ======================

    def get_identity_context(self):

        memories = (
            self.identity.get_all()
        )

        context = []

        for memory in memories:

            context.append(
                f"{memory['key']}: "
                f"{memory['value']}"
            )

        return context

    def get_relationship_context(self):

        people = (
            self.relationships
            .get_all_people()
        )

        context = []

        for person in people:

            confidence = (
                person["confidence"]
            )

            should_confirm = (
                confidence < 0.60
            )

            if should_confirm:

                text = (
                    f"{person['name']} "
                    f"(confirmar status)"
                )

            else:

                text = (
                    f"{person['name']} "
                    f"é "
                    f"{person['relationship_type']}"
                )

            context.append(text)

        return context

    def get_episodic_context(
        self,
        limit=5
    ):

        events = (
            self.episodic
            .get_recent_events(limit)
        )

        context = []

        for event in events:

            context.append(
                event["summary"]
            )

        return context

    # ======================
    # FULL CONTEXT
    # ======================

    def build_memory_context(self):

        identity = (
            self.get_identity_context()
        )

        relationships = (
            self
            .get_relationship_context()
        )

        episodic = (
            self
            .get_episodic_context()
        )

        context = f"""
IDENTIDADE:
{chr(10).join(identity)}

RELACIONAMENTOS:
{chr(10).join(relationships)}

MEMÓRIAS RECENTES:
{chr(10).join(episodic)}
"""

        return context
    

    def learn_from_message(self,message: str):
        """
        Aprende automaticamente
        com mensagens do usuário.
        """

        extracted = (
            self.extractor
            .extract(message)
        )

        detected_emotion = (
            self.emotion
            .analyze(message)
)

        # ======================
        # identidade
        # ======================

        for memory in (
            extracted["identity"]
        ):

            self.save_identity(
                key=memory["key"],
                value=memory["value"]
            )

        # ======================
        # relacionamentos
        # ======================

        for person in (
            extracted[
                "relationships"
            ]
        ):

            self.save_relationship(

                name=person["name"],

                relationship_type=
                person[
                    "relationship_type"
                ],

                emotional_context=
                person[
                    "emotional_context"
                ]
            )

        # ======================
        # eventos
        # ======================

        for event in (
            extracted["events"]
        ):

            self.save_event(

                summary=
                event["summary"],

                emotion=(event["emotion"]or detected_emotion),

                importance=
                event["importance"],

                tags=
                event["tags"]
            )

    def get_relevant_context(self,user_message: str):
        """
        Busca memórias relevantes
        para o assunto atual.
        """

        user_message = (
            user_message.lower()
        )

        relevant_context = []

        # ======================
        # NAMORO
        # ======================

        relationship_keywords = [

            "namoro",
            "namorada",
            "relacionamento",
            "amor",
            "briga",
            "ciúmes",
            "termino",
            "saudade"
        ]

        if any(
            word in user_message
            for word in relationship_keywords
        ):

            people = (
                self.relationships
                .get_all_people()
            )

            for person in people:

                relevant_context.append(

                    f"{person['name']} "
                    f"é "
                    f"{person['relationship_type']}"
                )

            events = (
                self.episodic
                .get_recent_events(3)
            )

            for event in events:

                if event["emotion"]:

                    relevant_context.append(

                        f"Evento recente: "
                        f"{event['summary']}"
                    )

        # ======================
        # TECNOLOGIA / LINUX
        # ======================

        tech_keywords = [

            "linux",
            "pc",
            "computador",
            "python",
            "programação",
            "ia",
            "site",
            "codigo",
            "erro"
        ]

        if any(
            word in user_message
            for word in tech_keywords
        ):

            identities = (
                self.identity
                .get_all()
            )

            for memory in identities:

                if memory[
                    "category"
                ] in [

                    "general",
                    "tech"
                ]:

                    relevant_context.append(

                        f"{memory['key']}: "
                        f"{memory['value']}"
                    )

        # ======================
        # FALLBACK
        # ======================

        if not relevant_context:

            identities = (
                self.identity
                .get_all()
            )

            for memory in identities[:5]:

                relevant_context.append(

                    f"{memory['key']}: "
                    f"{memory['value']}"
                )

        return "\n".join(
            relevant_context
        )
    
    def learn_from_conversation(
        self,
        user_message,
        ai_response
    ):

        summary = (
            self.summarizer
            .summarize(
                user_message,
                ai_response
            )
        )

        if summary:

            self.save_event(
                summary=summary,
                importance=0.5,
                tags="summary"
            )