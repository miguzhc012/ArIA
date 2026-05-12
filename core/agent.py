"""
core/agent.py

O orquestrador central do sistema. É o coração do assistente.

Responsabilidades desta fase (Fase 1):
- Receber input do usuário
- Construir o prompt com contexto (por enquanto, contexto básico)
- Enviar para o Ollama
- Retornar a resposta

O que este arquivo NÃO faz ainda (virá nas próximas fases):
- Buscar memórias (Fase 2)
- Resumir conversas (Fase 3)
- Usar ferramentas (Fase 5+)

Isso é intencional. Construímos em camadas.
Cada fase adiciona capacidade sem reescrever o que já funciona.
"""

from tools.package_tool import (PackageTool)
from tools.terminal_tool import (TerminalTool)
from memory.manager import MemoryManager
from typing import Generator, Optional
from core.ollama_client import OllamaClient
from core.session import Session
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger(__name__)


# System prompt base do assistente
# Isso define a "personalidade" fundamental.
# Nas próximas fases, vamos injetar memórias aqui dinamicamente.
BASE_SYSTEM_PROMPT = """Você é {name}, um assistente pessoal local e privado.


FERRAMENTAS DISPONÍVEIS:

1. PACKAGE_TOOL
Use quando o usuário quiser instalar programas Linux.

Formato:
[TOOL:PACKAGE]
query=nome_programa
action=install

Exemplo:
Usuário:
"instala obs"

Resposta:
[TOOL:PACKAGE]
query=obs
action=install


2. TERMINAL_TOOL
Use para informações do sistema Linux.

Formato:
[TOOL:TERMINAL]
command=comando

Exemplo:
Usuário:
"qual meu ip?"

Resposta:
[TOOL:TERMINAL]
command=ip a

IMPORTANTE:
Se usar ferramenta,
responda SOMENTE com o bloco.
Sem explicações extras.

Características fundamentais:
- Você é direto, honesto e genuinamente útil
- Você se lembra do contexto da conversa atual
- Você fala de forma natural, sem ser excessivamente formal
- Você admite quando não sabe algo em vez de inventar
- Você está rodando 100% localmente — total privacidade

Idioma: responda sempre em português brasileiro, a menos que o usuário escreva em outro idioma.
"""


class Agent:
    """
    Orquestrador principal do assistente.
    
    Esta classe coordena todos os componentes:
    - OllamaClient: comunicação com o LLM
    - Session: histórico da conversa atual
    - (futuro) MemoryManager: memória persistente
    - (futuro) ToolManager: ferramentas
    """
    
    def __init__(self):
        self.terminal_tool = (TerminalTool())
        self.memory = MemoryManager()
        self.client = OllamaClient()
        self.session = Session()
        self.package_tool = (PackageTool())
        self.pending_action = None

        
        logger.info(
            "Agent iniciado | modelo: %s | sessão: %s",
            settings.ollama.model,
            self.session.id
        )
    
    def should_use_package_tool(
    self,
    user_message
):

        text = (
            user_message
            .lower()
        )

        install_words = [

            "instala",
            "instalar",
            "baixar",
            "adiciona",
            "instale"
        ]

        return any(

            word in text
            for word
            in install_words
        )


    def extract_package_name(
        self,
        user_message
    ):

        text = (
            user_message
            .lower()
        )

        words_to_remove = [

            "instala",
            "instalar",
            "baixar",
            "adiciona",
            "instale"
        ]

        for word in (
            words_to_remove
        ):

            text = (
                text.replace(
                    word,
                    ""
                )
            )

        return (
            text.strip()
        )

    def _build_system_prompt(self,user_input: str):

        memory_context = (
            self.memory
            .build_memory_context()
        )

        system_prompt = f"""
        Você é Aria, uma IA pessoal privada.

        Você acompanha o usuário ao longo do tempo.

        Você possui memória persistente e deve agir de forma natural e contextual.

        REGRAS IMPORTANTES:

        1. Quando perguntarem:
        "o que você sabe sobre mim?"

        Responda APENAS com informações
        que realmente existem na memória.

        2. Nunca invente fatos.

        3. Seja natural.
        Não fale como banco de dados.

        4. Se souber pouco, admita.

        5. Fale diretamente com o usuário.

        Exemplo RUIM:
        "Eduarda é a namorada de Miguel"

        Exemplo BOM:
        "Até agora eu sei que seu nome é Miguel, você usa Linux e mencionou que sua namorada é Eduarda."

        6. Relacionamentos antigos podem mudar.
        Se algo parecer antigo ou incerto,
        pergunte naturalmente.

        7. Tente considerar
        o estado emocional
        recente do usuário
        quando apropriado.

        Se ele parecer frustrado,
        seja mais paciente.

        Se estiver feliz,
        pode ser mais leve.

        =========================
        SISTEMA DE FERRAMENTAS
        =========================

        Você possui ferramentas.

        NUNCA diga que não consegue acessar o sistema.

        Você ESTÁ rodando localmente
        no computador do usuário
        e TEM acesso ao terminal Linux.

        Quando o usuário pedir:

        - IP
        - rede
        - internet
        - cpu
        - ram
        - memória
        - wifi
        - processos
        - linux
        - terminal
        - apt
        - instalar programas

        VOCÊ DEVE responder APENAS
        com um bloco de ferramenta.

        NÃO explique.

        NÃO converse.

        NÃO responda normalmente.

        NÃO diga:
        "não posso"

        NÃO diga:
        "não tenho acesso"

        FORMATO OBRIGATÓRIO:

        TERMINAL:

        [TOOL:TERMINAL]
        command=comando_linux

        Exemplos:

        Usuário:
        qual meu ip

        Resposta:
        [TOOL:TERMINAL]
        command=ip a


        Usuário:
        quanta ram tenho

        Resposta:
        [TOOL:TERMINAL]
        command=free -h


        PACKAGE:

        [TOOL:PACKAGE]
        query=nome_programa
        action=install

        Usuário:
        instala obs

        Resposta:
        [TOOL:PACKAGE]
        query=obs
        action=install

        MEMÓRIA DO USUÁRIO:

        {memory_context}
        """
        return system_prompt
    
    
    
    def process_input(
    self,
    user_input: str
) -> Generator[str, None, None]:

    # ==========================
    # AÇÃO PENDENTE
    # ==========================

        if self.pending_action:

            if user_input.lower() in [

                "sim",
                "s",
                "yes"
            ]:

                action = (
                    self.pending_action
                )

                self.pending_action = None

                result = (
                    self.package_tool
                    .install_package(
                        action
                    )
                )

                yield result
                return

            elif user_input.lower() in [

                "nao",
                "não",
                "n",
                "cancelar"
            ]:

                self.pending_action = None

                yield (
                    "Instalação cancelada."
                )

                return

        # ==========================
        # PACKAGE TOOL
        # ==========================

        if self.should_use_package_tool(
            user_input
        ):

            package_name = (
                self.extract_package_name(
                    user_input
                )
            )

            search = (
                self.package_tool
                .search_package(
                    package_name
                )
            )

            package = (

                self.package_tool
                .extract_best_match(

                    search,
                    package_name
                )
            )

            if package:

                self.pending_action = (
                    package
                )

                yield (
                    f"Encontrei "
                    f"{package}.\n"
                    f"Deseja instalar?"
                )

                return

            yield (
                "Não encontrei "
                "nenhum pacote."
            )

            return

        # ==========================
        # MEMÓRIA
        # ==========================

        self.memory.learn_from_message(
            user_input
        )

        # ==========================
        # HISTÓRICO
        # ==========================

        self.session.add_user_message(
            user_input
        )

        logger.info(
            "Processando input "
            "(sessão %s, msg #%d)",
            self.session.id,
            self.session.get_message_count()
        )

        # ==========================
        # PROMPT
        # ==========================

        system_prompt = (
            self._build_system_prompt(
                user_input
            )
        )

        messages = (
            self.session
            .get_messages_for_llm()
        )

        # ==========================
        # LLM STREAM
        # ==========================

        full_response = []

        for chunk in self.client.chat_stream(
            messages,
            system_prompt
        ):

            full_response.append(
                chunk
            )

            yield chunk

        # ==========================
        # SALVAR RESPOSTA
        # ==========================

        complete_response = (
            "".join(
                full_response
            )
        )

        if complete_response:

            self.session.add_assistant_message(
                complete_response
            )

            self.memory.learn_from_conversation(
                user_input,
                complete_response
            )

            logger.info(
                "Resposta gerada | %d tokens aprox.",
                len(
                    complete_response.split()
                )
            )
        
        tool = (
            self.parse_tool_call(
                complete_response
            )
        )

        if tool:

            # PACKAGE
            if tool["tool"] == "package":

                search = (
                    self.package_tool
                    .search_package(
                        tool["query"]
                    )
                )

                package = (

                    self.package_tool
                    .extract_best_match(
                        search,
                        tool["query"]
                    )
                )

                if package:

                    self.pending_action = (
                        package
                    )

                    yield (
                        f"Encontrei "
                        f"{package}.\n"
                        f"Deseja instalar?"
                    )

                    return

            # TERMINAL
            if tool["tool"] == "terminal":

                result = (
                    self.terminal_tool
                    .execute_command(
                        tool["command"]
                    )
                )

                yield result
                return
    
    def handle_command(self, command: str) -> Optional[str]:
        """
        Processa comandos especiais do sistema (começam com /).
        
        Por que comandos separados de mensagens normais?
        Algumas ações são do sistema, não do LLM.
        '/limpar' não deve ser enviado ao modelo — deve limpar o histórico.
        '/modelos' não precisa de IA — só lista o que o Ollama tem.
        
        Args:
            command: string começando com /
            
        Returns:
            Mensagem de resposta do sistema, ou None se não reconhecido
        """
        
        command = command.strip().lower()
        
        if command == "/limpar":
            self.session.clear()
            return "Histórico da conversa limpo."
        
        elif command == "/sessao":
            duration = self.session.get_duration_minutes()
            count = self.session.get_message_count()
            return (
                f"Sessão: {self.session.id}\n"
                f"Mensagens: {count}\n"
                f"Duração: {duration:.1f} minutos\n"
                f"Modelo: {settings.ollama.model}"
            )
        
        elif command == "/modelos":
            models = self.client.get_available_models()
            if models:
                return "Modelos disponíveis:\n" + "\n".join(f"  - {m}" for m in models)
            return "Nenhum modelo encontrado. Você instalou algum modelo no Ollama?"
        
        elif command in ("/ajuda", "/help"):
            return (
                "Comandos disponíveis:\n"
                "  /limpar    — limpa o histórico da conversa atual\n"
                "  /sessao    — mostra informações da sessão\n"
                "  /modelos   — lista modelos disponíveis no Ollama\n"
                "  /ajuda     — mostra esta mensagem\n"
                "  sair       — encerra o assistente"
            )
        
        return None  # Comando não reconhecido
    
    def is_available(self) -> bool:
        """Verifica se o sistema está pronto para uso."""
        return self.client.is_available()
    
    def should_use_terminal(
    self,
    user_message
):

        text = (
            user_message.lower()
        )

        terminal_keywords = [

            "ip",
            "internet",
            "rede",
            "wifi",
            "wi-fi",
            "instalar",
            "apt",
            "nmap",
            "docker",
            "processo",
            "linux",
            "terminal",
            "cpu",
            "ram",
            "memoria"
        ]

        return any(
            word in text
            for word
            in terminal_keywords
        )

    def build_terminal_command(self,user_message):

        text = (
            user_message.lower()
        )

        if "ip" in text:

            return "ip a"

        if (
            "cpu" in text
            or
            "processador" in text
        ):

            return "lscpu"

        if (
            "ram" in text
            or
            "memoria" in text
        ):

            return "free -h"

        if (
            "internet" in text
            or
            "rede" in text
        ):

            return "ping -c 4 8.8.8.8"

        return None


        text = (
            user_message
            .lower()
        )

        install_words = [

            "instala",
            "instalar",
            "baixar",
            "adiciona"
        ]

        return any(
            word in text
            for word
            in install_words
        )
    
    def parse_tool_call(
    self,
    text
):

        if "[TOOL:PACKAGE]" in text:

            lines = (
                text.splitlines()
            )

            query = None
            action = None

            for line in lines:

                if line.startswith(
                    "query="
                ):
                    query = (
                        line
                        .replace(
                            "query=",
                            ""
                        )
                        .strip()
                    )

                if line.startswith(
                    "action="
                ):
                    action = (
                        line
                        .replace(
                            "action=",
                            ""
                        )
                        .strip()
                    )

            return {

                "tool":
                "package",

                "query":
                query,

                "action":
                action
            }

        if "[TOOL:TERMINAL]" in text:

            lines = (
                text.splitlines()
            )

            command = None

            for line in lines:

                if line.startswith(
                    "command="
                ):
                    command = (
                        line
                        .replace(
                            "command=",
                            ""
                        )
                        .strip()
                    )

            return {

                "tool":
                "terminal",

                "command":
                command
            }

        return None