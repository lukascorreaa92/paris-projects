"""Regras de negócio do app: prazos, status e preparação dos dados para a tela."""

from datetime import date, timedelta

import holidays

# ------------------------------------------------------------
# Configuração das regras (mudou a regra? mude só aqui)
# ------------------------------------------------------------
PRAZO_PLANILHAS_DIAS_UTEIS = 5
PRAZO_CADASTRO_DIAS_CORRIDOS = 30
DIAS_PARA_ALERTA = 2  # "vence em breve" quando faltar até 2 dias

# Feriados nacionais do Brasil (a biblioteca calcula os móveis, como a Sexta-feira Santa)
FERIADOS = holidays.Brazil()

# Nome da classe CSS de cada status (sem acento e sem espaço)
CLASSE_STATUS = {
    "INÍCIO": "inicio",
    "EM ANDAMENTO": "andamento",
    "FINALIZADO": "finalizado",
    "ATRASADO": "atrasado",
}


# ------------------------------------------------------------
# Funções de data
# ------------------------------------------------------------
def para_data(texto):
    """Converte '2026-11-20' em um objeto date. Vazio vira None."""
    return date.fromisoformat(texto) if texto else None


def eh_dia_util(dia):
    """Dia útil = segunda a sexta (weekday 0 a 4) e que não seja feriado."""
    return dia.weekday() < 5 and dia not in FERIADOS


def somar_dias_uteis(inicio, quantidade):
    """Avança 'quantidade' dias úteis a partir do dia seguinte ao início."""
    dia = inicio
    contados = 0
    while contados < quantidade:
        dia += timedelta(days=1)
        if eh_dia_util(dia):
            contados += 1
    return dia


def dias_texto(n):
    """1 -> '1 dia' / 3 -> '3 dias'."""
    return f"{n} dia" if n == 1 else f"{n} dias"


# ------------------------------------------------------------
# Avaliação de cada etapa
# ------------------------------------------------------------
def avaliar_etapa(nome, inicio, prazo, concluida, hoje, concluida_em=None):
    """Devolve um dicionário com a situação da etapa, pronto para a tela.

    classe: neutro | concluido | ok | alerta | atrasado (usada no CSS)
    atrasada: True/False (usada no cálculo do status do projeto)
    """
    etapa = {"nome": nome, "prazo": None, "texto": "", "classe": "neutro", "atrasada": False}

    if inicio is None:
        etapa["texto"] = "Não iniciada"
        return etapa

    etapa["prazo"] = prazo.isoformat()

    if concluida:
        etapa["classe"] = "concluido"
        if concluida_em and concluida_em > prazo:
            atraso = (concluida_em - prazo).days
            etapa["texto"] = f"Concluída com {dias_texto(atraso)} de atraso"
        else:
            etapa["texto"] = "Concluída"
        return etapa

    faltam = (prazo - hoje).days  # diferença entre duas datas, em dias

    if faltam < 0:
        etapa["texto"] = f"Atrasada há {dias_texto(-faltam)}"
        etapa["classe"] = "atrasado"
        etapa["atrasada"] = True
    elif faltam == 0:
        etapa["texto"] = "Vence hoje"
        etapa["classe"] = "alerta"
    elif faltam <= DIAS_PARA_ALERTA:
        etapa["texto"] = f"Vence em {dias_texto(faltam)}"
        etapa["classe"] = "alerta"
    else:
        etapa["texto"] = f"No prazo · faltam {dias_texto(faltam)}"
        etapa["classe"] = "ok"

    return etapa


def calcular_prazos(projeto, hoje):
    """Avalia as duas etapas com prazo e devolve uma lista com as duas."""

    # Planilhas: 5 dias ÚTEIS após o envio; concluída quando há data de devolução
    envio = para_data(projeto["planilhas_data_envio"])
    devolucao = para_data(projeto["planilhas_data_devolucao"])
    planilhas = avaliar_etapa(
        nome="Planilhas",
        inicio=envio,
        prazo=somar_dias_uteis(envio, PRAZO_PLANILHAS_DIAS_UTEIS) if envio else None,
        concluida=devolucao is not None,
        concluida_em=devolucao,
        hoje=hoje,
    )

    # Cadastro + treinamentos: 30 dias CORRIDOS; concluída quando a validação está CONCLUÍDO
    inicio_cadastro = para_data(projeto["data_inicio_cadastro"])
    cadastro = avaliar_etapa(
        nome="Cadastro + treinamentos",
        inicio=inicio_cadastro,
        prazo=inicio_cadastro + timedelta(days=PRAZO_CADASTRO_DIAS_CORRIDOS) if inicio_cadastro else None,
        concluida=projeto["validacao_cliente"] == "CONCLUÍDO",
        hoje=hoje,
    )

    return [planilhas, cadastro]


# ------------------------------------------------------------
# Status do projeto
# ------------------------------------------------------------
def calcular_status(projeto, prazos):
    """FINALIZADO manda; senão, qualquer etapa atrasada vira ATRASADO; senão, a fase."""
    if projeto["fase"] == "FINALIZADO":
        return "FINALIZADO"
    if any(etapa["atrasada"] for etapa in prazos):
        return "ATRASADO"
    return projeto["fase"]


def preparar_card(linha, hoje=None):
    """Transforma uma linha do banco num dicionário pronto para a tela."""
    hoje = hoje or date.today()

    projeto = dict(linha)
    projeto["prazos"] = calcular_prazos(projeto, hoje)
    projeto["status"] = calcular_status(projeto, projeto["prazos"])
    projeto["classe_status"] = CLASSE_STATUS[projeto["status"]]
    return projeto
