"""
main.py

Ponto de entrada do assistente pessoal.
Execute: python main.py

Este arquivo é propositalmente simples.
Sua única responsabilidade é:
1. Verificar se o ambiente está pronto
2. Criar o agente
3. Rodar o loop de chat
4. Tratar saída elegante (Ctrl+C, comando 'sair')

Toda a lógica real está no agent.py e nos módulos específicos.
"""
from database.schema import create_tables
import sys
from pathlib import Path

# Adiciona o diretório raiz ao Python path
# Isso permite importar 'from core.agent import Agent' em vez de
# 'from assistente.core.agent import Agent'
# É necessário porque executamos: python main.py (a partir da pasta raiz)
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from core.agent import Agent
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger(__name__)


def print_welcome():
    """Exibe mensagem de boas-vindas."""
    name = settings.assistant.name
    model = settings.ollama.model
    
    print("\n" + "─" * 60)
    print(f"  {name} — Assistente Pessoal Local")
    print(f"  Modelo: {model}")
    print("─" * 60)
    print("  Digite sua mensagem e pressione Enter.")
    print("  Comandos: /ajuda  /limpar  /sessao  /modelos")
    print("  Para sair: 'sair' ou Ctrl+C")
    print("─" * 60 + "\n")


def check_environment(agent: Agent) -> bool:
    """
    Verifica se o ambiente está configurado corretamente.
    
    Retorna False se algo estiver errado, com mensagem explicativa.
    """
    print("Verificando Ollama...", end=" ", flush=True)
    
    if not agent.is_available():
        print("❌ ERRO")
        print("\nNão foi possível conectar ao Ollama.")
        print("Certifique-se que o Ollama está instalado e rodando:")
        print("  1. Instale: https://ollama.ai")
        print("  2. Inicie: ollama serve")
        print(f"  3. Instale um modelo: ollama pull {settings.ollama.model}")
        return False
    
    print("✓ OK")
    return True


def run_chat_loop(agent: Agent):
    """
    Loop principal de chat.
    
    Fica em loop infinito aguardando input do usuário,
    processando e imprimindo a resposta.
    
    O loop termina quando:
    - Usuário digita 'sair'
    - Usuário pressiona Ctrl+C (KeyboardInterrupt)
    - Ocorre erro crítico
    """
    
    assistant_name = settings.assistant.name
    
    while True:
        try:
            # Aguarda input do usuário
            # O end="" e flush=True garantem que o cursor fique na mesma linha
            print("Você: ", end="", flush=True)
            user_input = input().strip()
            
            # Ignora entradas vazias (usuário só pressionou Enter)
            if not user_input:
                continue
            
            # Verifica se é comando para sair
            if user_input.lower() in ("sair", "exit", "quit", "q"):
                print(f"\n{assistant_name}: Até logo!\n")
                logger.info("Sessão encerrada pelo usuário")
                break
            
            # Verifica se é um comando do sistema (começa com /)
            if user_input.startswith("/"):
                response = agent.handle_command(user_input)
                if response:
                    print(f"\n{assistant_name}: {response}\n")
                else:
                    print(f"\n{assistant_name}: Comando não reconhecido. Digite /ajuda para ver os comandos.\n")
                continue
            
            # Processamento normal: envia para o LLM
            print(f"\n{assistant_name}: ", end="", flush=True)
            
            # Itera sobre os chunks do streaming
            # À medida que o modelo gera texto, imprimimos imediatamente
            # end="" e flush=True garantem que aparece sem quebras de linha extras
            for chunk in agent.process_input(user_input):
                print(chunk, end="", flush=True)
            
            # Quebra de linha após a resposta completa
            print("\n")
            
        except KeyboardInterrupt:
            # Ctrl+C — saída elegante
            print(f"\n\n{assistant_name}: Até logo!\n")
            logger.info("Sessão interrompida com Ctrl+C")
            break
            
        except EOFError:
            # EOF pode acontecer em pipes ou redirecionamento de entrada
            logger.info("EOF recebido, encerrando")
            break

def main():
    """Função principal — ponto de entrada."""
    create_tables()
    logger.info("Iniciando assistente pessoal")
    
    # Cria o agente (isso inicializa todos os componentes)
    try:
        agent = Agent()
    except Exception as e:
        print(f"\nErro ao iniciar o assistente: {e}")
        logger.critical("Falha ao criar Agent: %s", e)
        sys.exit(1)
    
    # Verifica ambiente
    if not check_environment(agent):
        sys.exit(1)
    
    # Exibe boas-vindas
    print_welcome()
    
    # Inicia o loop de chat
    run_chat_loop(agent)
    
    logger.info("Assistente encerrado normalmente")


# Este bloco garante que main() só é chamado quando executamos diretamente:
#   python main.py  ← main() é chamado
# Se alguém importar este arquivo:
#   import main     ← main() NÃO é chamado automaticamente
if __name__ == "__main__":
    main()
