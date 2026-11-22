"""Ponto de partida do programa para o dia a dia (e para o .exe).

O que ele faz, em ordem:
  1. Se o app já estiver aberto, só abre o navegador e sai.
  2. Cria o banco de dados, se ainda não existir.
  3. Abre o navegador no endereço do app.
  4. Liga o servidor (e fica ligado até você fechar a janela).
"""

import socket
import threading
import webbrowser

from app import app
from config import NOME_APP, PORTA
from database import DB_PATH, init_db

ENDERECO = f"http://127.0.0.1:{PORTA}"


def app_ja_esta_rodando():
    """Tenta conectar na porta: se conseguir, já tem um servidor ligado nela."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
        return conexao.connect_ex(("127.0.0.1", PORTA)) == 0


def abrir_navegador():
    webbrowser.open(ENDERECO)


if __name__ == "__main__":
    if app_ja_esta_rodando():
        abrir_navegador()
    else:
        init_db()  # seguro rodar sempre: "CREATE TABLE IF NOT EXISTS"

        print("=" * 56)
        print(f"  {NOME_APP.upper()} está rodando")
        print(f"  Endereço ..........: {ENDERECO}")
        print(f"  Banco de dados ....: {DB_PATH}")
        print()
        print("  Para ENCERRAR o programa, feche esta janela.")
        print("=" * 56)

        # Abre o navegador 1,5 s depois, dando tempo de o servidor ligar
        threading.Timer(1.5, abrir_navegador).start()

        app.run(host="127.0.0.1", port=PORTA, debug=False)
