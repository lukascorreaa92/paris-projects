"""Busca, filtros e ordenação da lista de projetos."""

import unicodedata

# Ordem em que as situações aparecem no painel de filtros
STATUS_FILTRO = ["ATRASADO", "EM ANDAMENTO", "INÍCIO", "FINALIZADO"]

# Opções de ordenação: valor que vai na URL -> texto que aparece na tela
OPCOES_ORDEM = {
    "urgencia": "Urgência",
    "cliente": "Cliente (A–Z)",
    "inicio": "Início do projeto",
}

# Peso de cada status na ordenação por urgência (menor = aparece primeiro)
PESO_URGENCIA = {
    "ATRASADO": 0,
    "EM ANDAMENTO": 1,
    "INÍCIO": 2,
    "FINALIZADO": 3,
}

SEM_DATA = "9999-12-31"  # projetos sem data vão para o fim da fila


def normalizar(texto):
    """Deixa o texto comparável: minúsculo e sem acento. 'São Lucas' -> 'sao lucas'."""
    decomposto = unicodedata.normalize("NFD", texto or "")
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def chave_urgencia(projeto):
    """Critério de ordenação por urgência.

    1º) peso do status (ATRASADO antes de tudo)
    2º) o prazo pendente mais próximo (ou o mais vencido)
    3º) nome do cliente, para desempatar
    """
    prazos_pendentes = [
        etapa["prazo"]
        for etapa in projeto["prazos"]
        if etapa["prazo"] and etapa["classe"] in ("atrasado", "alerta", "ok")
    ]
    proximo_prazo = min(prazos_pendentes) if prazos_pendentes else SEM_DATA
    return (PESO_URGENCIA[projeto["status"]], proximo_prazo, normalizar(projeto["cliente"]))


def aplicar_filtros(projetos, busca="", status="", produto="", ordem="urgencia"):
    """Filtra e ordena a lista de projetos já preparados (com status calculado)."""
    termo = normalizar(busca)
    resultado = []

    for p in projetos:
        # Busca: procura no nome do cliente e no GP, ignorando acentos e maiúsculas
        if termo and termo not in normalizar(p["cliente"]) and termo not in normalizar(p["gp"]):
            continue
        if status and p["status"] != status:
            continue
        if produto and p["produto"] != produto:
            continue
        resultado.append(p)

    if ordem == "cliente":
        resultado.sort(key=lambda p: normalizar(p["cliente"]))
    elif ordem == "inicio":
        resultado.sort(key=lambda p: p["data_inicio_projeto"] or SEM_DATA)
    else:
        resultado.sort(key=chave_urgencia)

    return resultado
