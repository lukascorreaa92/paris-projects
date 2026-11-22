"""Descobre as pastas certas, rodando como script (python app.py) ou como .exe.

Quando o PyInstaller gera o .exe, ele "empacota" templates, static e schema.sql
dentro do executável. Ao abrir o .exe, esses arquivos são extraídos numa pasta
temporária (sys._MEIPASS). Já o banco de dados precisa ficar numa pasta
PERMANENTE: ao lado do .exe.
"""

import sys
from pathlib import Path

# sys.frozen só existe (e vale True) quando o programa está rodando como .exe
RODANDO_COMO_EXE = getattr(sys, "frozen", False)


def pasta_do_programa():
    """Onde estão templates/, static/ e schema.sql."""
    if RODANDO_COMO_EXE:
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def pasta_dos_dados():
    """Onde fica o arquivo do banco (implantacoes.db)."""
    if RODANDO_COMO_EXE:
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent
