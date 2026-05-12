"""
core/ollama_client.py

Cliente para comunicar com o Ollama via HTTP.

Por que HTTP e não uma biblioteca oficial?
O Ollama expõe uma API REST simples. Usar requests diretamente nos dá
controle total, sem depender de bibliotecas de terceiros que podem mudar.

Como o Ollama funciona:
  Você inicia o servidor: `ollama serve`
  Ele roda em localhost:11434
  Você envia POST para /api/chat com as mensagens
  Ele responde com o texto gerado

Há dois modos de resposta do Ollama:
  1. Streaming: retorna tokens à medida que gera (parece que o modelo "digita")
  2. Completo: aguarda tudo gerado e retorna de uma vez

Vamos usar streaming para dar feedback visual imediato ao usuário.
"""

import json
import requests
from typing import Generator, Optional
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger(__name__)


class OllamaClient:
    """
    Gerencia comunicação com o servidor Ollama local.
    
    Esta classe encapsula toda a lógica de HTTP — o resto do sistema
    não precisa saber que estamos usando requests ou como a API funciona.
    Isso é o princípio de encapsulamento.
    """
    
    def __init__(self):
        self.base_url = settings.ollama.base_url
        self.model = settings.ollama.model
        self.timeout = settings.ollama.timeout
        
    def is_available(self) -> bool:
        """
        Verifica se o servidor Ollama está rodando.
        
        Tenta conectar no endpoint /api/tags que lista modelos disponíveis.
        Se falhar, o servidor não está acessível.
        
        Returns:
            True se Ollama está acessível, False caso contrário
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5  # Timeout curto: se não responder em 5s, está offline
            )
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            # Servidor não está rodando
            return False
        except Exception as e:
            logger.error("Erro inesperado ao verificar Ollama: %s", e)
            return False
    
    def get_available_models(self) -> list[str]:
        """
        Retorna lista de modelos instalados no Ollama.
        
        Returns:
            Lista de nomes de modelos, ex: ["llama3:latest", "mistral:latest"]
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()  # Lança exceção se status não for 2xx
            
            data = response.json()
            # A API retorna: {"models": [{"name": "llama3:latest", ...}, ...]}
            return [model["name"] for model in data.get("models", [])]
            
        except Exception as e:
            logger.error("Erro ao listar modelos: %s", e)
            return []
    
    def chat_stream(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Envia mensagens para o modelo e retorna a resposta em streaming.
        
        Streaming significa que o modelo retorna pedaços de texto à medida
        que gera, em vez de esperar terminar tudo. Isso dá a sensação de
        que o modelo está "digitando" em tempo real.
        
        Args:
            messages: histórico de mensagens no formato:
                      [{"role": "user", "content": "..."}, 
                       {"role": "assistant", "content": "..."}]
            system_prompt: instrução de sistema (personalidade, contexto, memória)
            
        Yields:
            Pedaços de texto à medida que são gerados
            
        Como usar:
            for chunk in client.chat_stream(messages):
                print(chunk, end="", flush=True)
        """
        
        # Monta o payload (dados) para enviar à API
        payload = {
    "model": settings.ollama.model,
    "messages": messages,
    "stream": True,

    "options": {

        # MUITO importante
        "num_ctx": 768,

        # menos texto
        "num_predict": 120,

        # criatividade ok
        "temperature": 0.7,

        # teu CPU é dual core
        "num_thread": 2,

        # acelera sampling
        "top_k": 20,

        # ajuda velocidade
        "top_p": 0.8
    }
}
        
        # Se há um system prompt, adiciona no início das mensagens
        # O Ollama aceita uma mensagem especial com role="system"
        if system_prompt:
            payload["messages"] = [
                {"role": "system", "content": system_prompt}
            ] + messages
        
        logger.debug("Enviando %d mensagens para o modelo %s", len(messages), self.model)
        
        try:
            # stream=True no requests significa que não carregamos tudo na memória
            # Recebemos linha por linha conforme chegam
            with requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=self.timeout
            ) as response:
                response.raise_for_status()
                
                # O Ollama retorna uma linha JSON por vez
                # Cada linha tem: {"message": {"content": "pedaço de texto"}, "done": false}
                # A última linha tem: {"done": true}
                for line in response.iter_lines():
                    if not line:
                        continue  # Pula linhas vazias
                    
                    try:
                        # Decodifica o JSON da linha
                        chunk_data = json.loads(line.decode("utf-8"))
                        
                        # Verifica se ainda há conteúdo a processar
                        if chunk_data.get("done", False):
                            logger.debug("Streaming concluído")
                            break
                        
                        # Extrai o pedaço de texto gerado
                        # O caminho no JSON é: message -> content
                        content = chunk_data.get("message", {}).get("content", "")
                        if content:
                            yield content
                            
                    except json.JSONDecodeError as e:
                        logger.warning("Linha inválida do streaming: %s", e)
                        continue
                        
        except requests.exceptions.Timeout:
            error_msg = f"\n[Erro: O modelo demorou mais de {self.timeout}s para responder]"
            logger.error("Timeout ao aguardar resposta do Ollama")
            yield error_msg
            
        except requests.exceptions.ConnectionError:
            error_msg = "\n[Erro: Não foi possível conectar ao Ollama. Ele está rodando?]"
            logger.error("Erro de conexão com Ollama")
            yield error_msg
            
        except Exception as e:
            error_msg = f"\n[Erro inesperado: {str(e)}]"
            logger.error("Erro inesperado no chat_stream: %s", e)
            yield error_msg
    
    def chat(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Versão não-streaming: aguarda resposta completa e retorna string.
        
        Útil para tarefas internas que não precisam de feedback visual
        (ex: gerar resumo de conversa em background).
        
        Returns:
            Resposta completa como string
        """
        chunks = []
        for chunk in self.chat_stream(messages, system_prompt):
            chunks.append(chunk)
        return "".join(chunks)
