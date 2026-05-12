"""
core/session.py

Gerencia o estado de uma conversa (sessão).

O que é uma sessão?
É o conjunto de mensagens trocadas em uma "conversa".
Quando você fecha o terminal e abre de novo, começa uma nova sessão.

Por que separar sessão do agente?
O agente sabe COMO processar mensagens.
A sessão sabe O QUE foi dito até agora.
São responsabilidades diferentes.

Analogia: o agente é o garçom, a sessão é o bloco de pedidos.
"""

from datetime import datetime
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger(__name__)


class Message:
    """
    Representa uma única mensagem na conversa.
    
    Por que uma classe e não só um dicionário?
    - Validação: garante que role é válido
    - Métodos utilitários (to_dict, __repr__)
    - Mais legível no código que message["role"]
    """
    
    VALID_ROLES = {"user", "assistant", "system"}
    
    def __init__(self, role: str, content: str):
        if role not in self.VALID_ROLES:
            raise ValueError(f"Role inválido: {role}. Use: {self.VALID_ROLES}")
        
        self.role = role
        self.content = content
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        """
        Converte para o formato que o Ollama espera.
        O Ollama aceita: {"role": "user", "content": "..."}
        """
        return {"role": self.role, "content": self.content}
    
    def __repr__(self) -> str:
        """Representação legível para debug."""
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Message(role={self.role}, content={preview!r})"


class Session:
    """
    Mantém o histórico de mensagens da conversa atual.
    
    Responsabilidades:
    - Armazenar mensagens em ordem
    - Limitar tamanho do histórico (para não sobrecarregar o contexto)
    - Fornecer mensagens no formato correto para o LLM
    """
    
    def __init__(self):
        self._messages: list[Message] = []
        self.started_at = datetime.now()
        self.id = self.started_at.strftime("%Y%m%d_%H%M%S")
        
        logger.info("Nova sessão iniciada: %s", self.id)
    
    def add_user_message(self, content: str) -> None:
        """Adiciona mensagem do usuário ao histórico."""
        msg = Message("user", content)
        self._messages.append(msg)
        logger.debug("Mensagem do usuário adicionada: %s", msg)
    
    def add_assistant_message(self, content: str) -> None:
        """Adiciona mensagem do assistente ao histórico."""
        msg = Message("assistant", content)
        self._messages.append(msg)
        logger.debug("Mensagem do assistente adicionada: %s", msg)
    
    def get_messages_for_llm(self) -> list[dict]:
        """
        Retorna as mensagens no formato que o Ollama espera.
        
        Aplica a limitação de max_history_messages para não sobrecarregar
        o contexto do modelo. Sempre pega as mensagens mais recentes.
        
        Returns:
            Lista de dicts: [{"role": "...", "content": "..."}, ...]
        """
        max_msgs = settings.assistant.max_history_messages
        
        # Pega as últimas N mensagens
        # -max_msgs: pega do final, sem limite superior = até o fim
        recent = self._messages[-max_msgs:]
        
        return [msg.to_dict() for msg in recent]
    
    def get_message_count(self) -> int:
        """Retorna quantas mensagens existem na sessão atual."""
        return len(self._messages)
    
    def clear(self) -> None:
        """
        Limpa o histórico da sessão.
        Útil para começar um assunto novo sem fechar o terminal.
        """
        self._messages.clear()
        logger.info("Histórico da sessão %s limpo", self.id)
    
    def get_duration_minutes(self) -> float:
        """Retorna há quantos minutos a sessão está ativa."""
        delta = datetime.now() - self.started_at
        return delta.total_seconds() / 60
    
    def __repr__(self) -> str:
        return f"Session(id={self.id}, messages={len(self._messages)})"
