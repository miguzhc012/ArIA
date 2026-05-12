"""
config/settings.py

Configurações centralizadas do sistema.
Altere aqui para mudar comportamento global — não espalhe configs pelo código.

Por que dataclass? É uma classe Python que gera automaticamente __init__, __repr__
e outras funções. Mais limpo que um dicionário, com tipagem explícita.
"""

from dataclasses import dataclass, field
from pathlib import Path

# Diretório raiz do projeto (onde este arquivo está, dois níveis acima)
# Path(__file__) = caminho deste arquivo
# .parent = pasta config/
# .parent.parent = pasta assistente/ (raiz do projeto)
ROOT_DIR = Path(__file__).parent.parent


@dataclass
class OllamaConfig:
    """Configurações do servidor Ollama local."""
    
    # URL base do Ollama. Por padrão roda em localhost:11434
    base_url: str = "http://localhost:11434"
    
    # Modelo a usar. Troque aqui para mudar o modelo globalmente.
    # Opções comuns: "llama3", "mistral", "phi3", "gemma2"
    model: str = "qwen2.5:1.5b"
    
    # Timeout em segundos para aguardar resposta do modelo.
    # Modelos grandes podem demorar mais para responder.
    timeout: int = 120
    
    # Temperatura controla a "criatividade" da resposta.
    # 0.0 = determinístico e conservador
    # 1.0 = criativo e variado
    # Para um assistente pessoal, valores entre 0.6 e 0.8 funcionam bem.
    temperature: float = 0.7


@dataclass
class DatabaseConfig:
    """Configurações do banco de dados SQLite."""
    
    # Caminho do arquivo .db dentro do projeto
    path: Path = ROOT_DIR / "database" / "assistente.db"
    
    # Nível de WAL (Write-Ahead Logging): permite leituras e escritas simultâneas.
    # Para uso pessoal não é crítico, mas é boa prática.
    wal_mode: bool = True


@dataclass
class LogConfig:
    """Configurações de log."""
    
    # Pasta onde os logs serão salvos
    directory: Path = ROOT_DIR / "logs"
    
    # Nível de log: DEBUG, INFO, WARNING, ERROR
    # DEBUG mostra tudo (útil para desenvolvimento)
    # INFO mostra apenas eventos importantes
    level: str = "INFO"
    
    # Nome do arquivo de log (um por dia)
    filename: str = "assistente.log"


@dataclass
class AssistantConfig:
    """Configurações gerais do assistente."""
    
    # Nome do assistente (aparece nos logs e prompts)
    name: str = "Aria"
    
    # Número máximo de mensagens no histórico da sessão atual.
    # Limitar evita que o contexto fique grande demais (caro em tokens).
    max_history_messages: int = 8
    
    # Quantas memórias relevantes injetar no prompt por padrão
    max_memory_context: int = 5


@dataclass
class Settings:
    """
    Configurações globais do sistema.
    
    Uso:
        from config.settings import settings
        print(settings.ollama.model)
        print(settings.db.path)
    """
    
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    log: LogConfig = field(default_factory=LogConfig)
    assistant: AssistantConfig = field(default_factory=AssistantConfig)


# Instância global — importada por todos os módulos
# Assim existe apenas um objeto Settings em todo o sistema
settings = Settings()
