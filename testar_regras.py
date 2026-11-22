"""Teste rápido das regras de prazo, com uma data "de hoje" fixa.

Rode com:  python testar_regras.py
Se tudo estiver certo, aparece "Todos os testes passaram!".
"""

from datetime import date

from regras import preparar_card, somar_dias_uteis

HOJE = date(2026, 11, 25)  # uma quarta-feira


def projeto(**campos):
    """Cria um projeto de teste com valores padrão + o que for informado."""
    base = {
        "fase": "EM ANDAMENTO",
        "planilhas_data_envio": None,
        "planilhas_data_devolucao": None,
        "data_inicio_cadastro": None,
        "validacao_cliente": "PENDENTE",
    }
    base.update(campos)
    return preparar_card(base, hoje=HOJE)


# 1) Dias úteis pulam fim de semana e feriado (20/11 = Consciência Negra)
#    Envio seg 16/11 -> 17, 18, 19, (20 feriado), (21-22 fds), 23, 24
assert somar_dias_uteis(date(2026, 11, 16), 5) == date(2026, 11, 24)

# 2) Planilha enviada em 16/11, sem devolução: prazo 24/11, hoje 25/11 -> ATRASADO
p = projeto(planilhas_data_envio="2026-11-16")
assert p["status"] == "ATRASADO", p["status"]
assert p["prazos"][0]["texto"] == "Atrasada há 1 dia"

# 3) Mesma planilha, mas devolvida: etapa concluída, status volta a ser a fase
p = projeto(planilhas_data_envio="2026-11-16", planilhas_data_devolucao="2026-11-23")
assert p["status"] == "EM ANDAMENTO"
assert p["prazos"][0]["texto"] == "Concluída"

# 4) Devolvida depois do prazo: concluída, mas registra o atraso
p = projeto(planilhas_data_envio="2026-11-16", planilhas_data_devolucao="2026-11-25")
assert p["prazos"][0]["texto"] == "Concluída com 1 dia de atraso"

# 5) Cadastro iniciado há 31 dias, validação pendente -> ATRASADO
p = projeto(data_inicio_cadastro="2026-10-25")
assert p["status"] == "ATRASADO"

# 6) Cadastro vencendo em 2 dias -> alerta, mas ainda não atrasado
p = projeto(data_inicio_cadastro="2026-10-28")
assert p["prazos"][1]["classe"] == "alerta" and p["status"] == "EM ANDAMENTO"

# 7) Validação CONCLUÍDO encerra a etapa de cadastro
p = projeto(data_inicio_cadastro="2026-10-01", validacao_cliente="CONCLUÍDO")
assert p["status"] == "EM ANDAMENTO"

# 8) FINALIZADO sempre vence, mesmo com etapa estourada
p = projeto(fase="FINALIZADO", planilhas_data_envio="2026-11-01")
assert p["status"] == "FINALIZADO"

print("Todos os testes passaram!")
