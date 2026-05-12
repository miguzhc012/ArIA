"""
config/logger.py

Sistema de logging centralizado.

Por que logging ao invés de print()?
- print() não tem nível (debug vs erro vs info)
- print() não salva em arquivo
- print() não tem timestamp
- Em produção, você desliga DEBUG sem apagar código

Logging é uma das práticas mais importantes em qualquer sistema sério.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Cria e configura um logger com o nome do módulo.
    
    Uso:
        from config.logger import setup_logger
        logger = setup_logger(__name__)
        logger.info("Sistema iniciado")
        logger.error("Algo deu errado: %s", erro)
    
    Args:
        name: geralmente __name__ do módulo que está chamando
        
    Returns:
        Logger configurado com handlers para arquivo e terminal
    """
    
    # Garante que a pasta de logs existe
    # exist_ok=True não gera erro se já existir
    settings.log.directory.mkdir(parents=True, exist_ok=True)
    
    # Pega ou cria logger com esse nome
    # Se já existe um logger com esse nome, retorna o mesmo (sem duplicar handlers)
    logger = logging.getLogger(name)
    
    # Evita adicionar handlers duplicados se a função for chamada mais de uma vez
    if logger.handlers:
        return logger
    
    # Define o nível mínimo de mensagens que serão processadas
    level = getattr(logging, settings.log.level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Formato das mensagens de log
    # %(asctime)s    = data/hora
    # %(name)s       = nome do módulo (ex: core.agent)  
    # %(levelname)s  = nível (INFO, ERROR, etc)
    # %(message)s    = a mensagem em si
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler 1: escreve no terminal (stdout)
    # Útil durante desenvolvimento para ver o que está acontecendo
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    # Terminal só mostra WARNING ou mais grave (não polui a tela do chat)
    console_handler.setLevel(logging.WARNING)
    
    # Handler 2: escreve em arquivo com data no nome
    # Ex: logs/assistente_2024-01-15.log
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = settings.log.directory / f"assistente_{today}.log"
    
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    # Arquivo salva TUDO (nível configurado em settings)
    file_handler.setLevel(level)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
