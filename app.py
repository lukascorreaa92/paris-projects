import secrets
from datetime import date, datetime

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

import opcoes
from caminhos import pasta_do_programa
from config import HOSTS_PERMITIDOS, NOME_APP, carregar_chave_secreta
from database import atualizar_projeto, buscar_projeto, inserir_projeto, listar_projetos
from filtros import OPCOES_ORDEM, STATUS_FILTRO, aplicar_filtros
from regras import CLASSE_STATUS, preparar_card
from validacao import validar_projeto

app = Flask(
    __name__,
    template_folder=str(pasta_do_programa() / "templates"),
    static_folder=str(pasta_do_programa() / "static"),
)

# ------------------------------------------------------------
# Segurança
# ------------------------------------------------------------
# Chave secreta própria de cada instalação, guardada fora do código
app.config["SECRET_KEY"] = carregar_chave_secreta()

# O cookie de sessão não é enviado em formulários vindos de outros sites
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True


def gerar_csrf_token():
    """Cria (uma vez por sessão) o token que vai escondido nos formulários."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


@app.before_request
def proteger_requisicoes():
    """Roda antes de TODA requisição."""

    # 1) Só aceita acesso pelo próprio computador (bloqueia DNS rebinding)
    host = request.host.split(":")[0]
    if host not in HOSTS_PERMITIDOS:
        abort(400, description="Endereço não permitido.")

    # 2) Todo POST precisa trazer o token CSRF correto
    if request.method == "POST":
        token_enviado = request.form.get("csrf_token", "")
        token_da_sessao = session.get("csrf_token", "")
        if not token_da_sessao or not secrets.compare_digest(token_enviado, token_da_sessao):
            abort(400, description="Formulário recusado por segurança. "
                                   "Volte, recarregue a página e tente de novo.")


@app.after_request
def cabecalhos_de_seguranca(resposta):
    """Acrescenta cabeçalhos de segurança em TODA resposta."""
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["Referrer-Policy"] = "no-referrer"
    return resposta


# ------------------------------------------------------------
# Filtros de template: funções que formatam valores no HTML
# ------------------------------------------------------------
@app.template_filter("data_br")
def data_br(valor):
    """Converte '2026-11-20' em '20/11/2026'. Sem data, mostra um traço."""
    if not valor:
        return "—"
    return date.fromisoformat(valor).strftime("%d/%m/%Y")


@app.template_filter("data_hora_br")
def data_hora_br(valor):
    """Converte '2026-11-20 18:22:29' em '20/11/2026 às 18:22'."""
    if not valor:
        return "—"
    return datetime.fromisoformat(valor).strftime("%d/%m/%Y às %H:%M")


# ------------------------------------------------------------
# Variáveis disponíveis em TODOS os templates
# ------------------------------------------------------------
@app.context_processor
def variaveis_globais():
    return {
        "nome_app": NOME_APP,
        "opcoes": opcoes,
        "status_filtro": STATUS_FILTRO,
        "opcoes_ordem": OPCOES_ORDEM,
        "classe_status": CLASSE_STATUS,
        "csrf_token": gerar_csrf_token,
    }


# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
def lista_de_projetos():
    """Todos os projetos já preparados (status, cor). Usada na lista lateral e nos cards."""
    return [preparar_card(linha) for linha in listar_projetos()]


def projeto_ou_404(projeto_id):
    """Busca o projeto; se não existir, interrompe com a página 'Não encontrado'."""
    linha = buscar_projeto(projeto_id)
    if linha is None:
        abort(404)
    return linha


# ------------------------------------------------------------
# Rotas
# ------------------------------------------------------------
@app.route("/")
def inicio():
    tem_logo = (pasta_do_programa() / "static" / "img" / "logo.png").exists()
    return render_template("inicio.html", tem_logo=tem_logo)


@app.route("/projetos")
def projetos():
    # Lê os filtros da URL. Ex.: /projetos?busca=lucas&status=ATRASADO&ordem=urgencia
    filtros = {
        "busca": request.args.get("busca", "").strip(),
        "status": request.args.get("status", ""),
        "produto": request.args.get("produto", ""),
        "ordem": request.args.get("ordem", "urgencia"),
    }
    todos = lista_de_projetos()
    lista = aplicar_filtros(todos, **filtros)
    return render_template("projetos.html", projetos=lista, total=len(todos), filtros=filtros)


@app.route("/projetos/<int:projeto_id>")
def detalhe_projeto(projeto_id):
    projeto = preparar_card(projeto_ou_404(projeto_id))
    lateral = aplicar_filtros(lista_de_projetos())  # lista lateral por urgência
    return render_template("projeto_detalhe.html", projeto=projeto, projetos=lateral)


@app.route("/projetos/novo", methods=["GET", "POST"])
def novo_projeto():
    voltar = url_for("projetos")

    # POST = o usuário clicou em "Salvar"
    if request.method == "POST":
        dados, erros = validar_projeto(request.form)

        if erros:
            for erro in erros:
                flash(erro, "erro")
            # Mostra o formulário de novo, com o que a pessoa já tinha digitado
            return render_template(
                "projeto_form.html", projeto=request.form, titulo="Novo projeto", voltar=voltar
            )

        inserir_projeto(dados)
        flash(f"Projeto '{dados['cliente']}' cadastrado com sucesso!", "sucesso")
        return redirect(voltar)

    # GET = a pessoa só abriu a página: formulário vazio
    return render_template("projeto_form.html", projeto={}, titulo="Novo projeto", voltar=voltar)


@app.route("/projetos/<int:projeto_id>/editar", methods=["GET", "POST"])
def editar_projeto(projeto_id):
    linha = projeto_ou_404(projeto_id)
    voltar = url_for("detalhe_projeto", projeto_id=projeto_id)
    titulo = f"Editar · {linha['cliente']}"

    if request.method == "POST":
        dados, erros = validar_projeto(request.form)

        if erros:
            for erro in erros:
                flash(erro, "erro")
            return render_template(
                "projeto_form.html", projeto=request.form, titulo=titulo, voltar=voltar
            )

        atualizar_projeto(projeto_id, dados)
        flash("Alterações salvas!", "sucesso")
        return redirect(voltar)

    # GET: formulário já preenchido com os dados atuais do projeto
    return render_template("projeto_form.html", projeto=dict(linha), titulo=titulo, voltar=voltar)


# Modo DESENVOLVIMENTO: "python app.py" (recarrega sozinho e mostra erros detalhados).
# Escuta só em 127.0.0.1, então o depurador nunca fica exposto na rede.
# Para USAR o app no dia a dia, rode "python iniciar.py" ou o .exe.
if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
