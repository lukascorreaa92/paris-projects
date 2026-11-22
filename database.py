import sqlite3

from caminhos import pasta_do_programa, pasta_dos_dados

# Caminho do arquivo do banco e do script que cria as tabelas
DB_PATH = pasta_dos_dados() / "implantacoes.db"
SCHEMA_PATH = pasta_do_programa() / "schema.sql"


def get_connection():
    """Abre uma conexão com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    # Permite acessar as colunas pelo nome: projeto["cliente"]
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas do banco a partir do schema.sql."""
    conn = get_connection()
    try:
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()
    print(f"Banco pronto em: {DB_PATH}")


def inserir_projeto(dados):
    """Grava um novo projeto e devolve o id gerado.

    'dados' é o dicionário que sai do validar_projeto().
    """
    colunas = ", ".join(dados.keys())          # cliente, produto, infra_url, ...
    marcadores = ", ".join("?" for _ in dados)  # ?, ?, ?, ...
    sql = f"INSERT INTO projetos ({colunas}) VALUES ({marcadores})"

    conn = get_connection()
    try:
        cursor = conn.execute(sql, list(dados.values()))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def listar_projetos():
    """Devolve todos os projetos, em ordem alfabética de cliente."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM projetos ORDER BY cliente COLLATE NOCASE"
        ).fetchall()
    finally:
        conn.close()


def buscar_projeto(projeto_id):
    """Devolve um projeto pelo id, ou None se não existir."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM projetos WHERE id = ?", (projeto_id,)
        ).fetchone()
    finally:
        conn.close()


def atualizar_projeto(projeto_id, dados):
    """Grava as alterações de um projeto existente."""
    atribuicoes = ", ".join(f"{coluna} = ?" for coluna in dados)  # cliente = ?, produto = ?, ...
    sql = (
        f"UPDATE projetos SET {atribuicoes}, "
        "atualizado_em = datetime('now', 'localtime') "
        "WHERE id = ?"
    )
    valores = list(dados.values()) + [projeto_id]

    conn = get_connection()
    try:
        conn.execute(sql, valores)
        conn.commit()
    finally:
        conn.close()


# Só roda quando você executa "python database.py" direto no terminal
if __name__ == "__main__":
    init_db()
