# Assistente Pessoal Local

Assistente de IA 100% local e privado, construído com Python e Ollama.

## Pré-requisitos

- Python 3.12+
- [Ollama](https://ollama.ai) instalado e rodando

## Instalação

```bash
# 1. Clone ou copie o projeto
cd assistente/

# 2. Crie um ambiente virtual (fortemente recomendado)
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Instale um modelo no Ollama (se ainda não tiver)
ollama pull llama3.2
# Alternativas: ollama pull mistral | ollama pull phi3

# 5. Garanta que o Ollama está rodando
ollama serve
```

## Uso

```bash
python main.py
```

## Comandos disponíveis no chat

| Comando    | Descrição                              |
|------------|----------------------------------------|
| `/ajuda`   | Lista todos os comandos                |
| `/limpar`  | Limpa o histórico da conversa atual    |
| `/sessao`  | Mostra informações da sessão           |
| `/modelos` | Lista modelos instalados no Ollama     |
| `sair`     | Encerra o assistente                   |

## Configuração

Edite `config/settings.py` para personalizar:

- `OllamaConfig.model` — modelo a usar (padrão: `llama3.2`)
- `OllamaConfig.temperature` — criatividade das respostas (0.0 a 1.0)
- `AssistantConfig.name` — nome do assistente (padrão: `Aria`)

## Estrutura do projeto

```
assistente/
├── main.py              ← ponto de entrada
├── core/
│   ├── agent.py         ← orquestrador principal
│   ├── session.py       ← histórico da conversa
│   └── ollama_client.py ← comunicação com Ollama
├── config/
│   ├── settings.py      ← configurações centralizadas
│   └── logger.py        ← sistema de logging
├── memory/              ← (Fase 2) memória persistente
├── database/            ← (Fase 2) SQLite
├── tools/               ← (Fase 5+) ferramentas
└── logs/                ← arquivos de log automáticos
```
