"""Configurações gerais do app. Para renomear o app, mude só NOME_APP."""

import secrets

from caminhos import pasta_dos_dados

NOME_APP = "Paris Projetos"

PORTA = 5000

# O app só aceita ser acessado por estes endereços (proteção contra DNS rebinding)
HOSTS_PERMITIDOS = {"127.0.0.1", "localhost"}

# Arquivo onde fica a chave secreta desta instalação (NUNCA vai para o GitHub)
ARQUIVO_CHAVE = pasta_dos_dados() / ".chave_secreta"


def carregar_chave_secreta():
    """Lê a chave secreta do arquivo; se não existir, gera uma nova e salva.

    Cada instalação (seu PC, o PC do seu amigo) tem a sua própria chave,
    criada no primeiro uso. Assim, nenhuma chave fica escrita no código.
    """
    if ARQUIVO_CHAVE.exists():
        chave = ARQUIVO_CHAVE.read_text(encoding="utf-8").strip()
        if chave:
            return chave

    chave = secrets.token_hex(32)  # 64 caracteres aleatórios
    ARQUIVO_CHAVE.write_text(chave, encoding="utf-8")
    return chave
