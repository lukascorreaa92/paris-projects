"""Listas de opções fixas do app.

Fonte única da verdade: o formulário monta os <select> a partir daqui
e a validação confere os valores recebidos contra estas mesmas listas.
"""

PRODUTOS = ["PACS", "RIS"]
FASES = ["INÍCIO", "EM ANDAMENTO", "FINALIZADO"]
VALIDACAO_CLIENTE = ["PENDENTE", "EM ANDAMENTO", "CONCLUÍDO"]
PASSAGEM_HOMOLOGACAO = ["ENVIAR E-MAIL DE PASSAGEM", "ENVIADO E-MAIL DE PASSAGEM"]
REUNIAO_IMPLANTADOR = ["PENDENTE", "CONCLUÍDO"]
TIPOS_PROJETO = ["AP", "NR", "AP+NR"]
TIPOS_SERVIDOR = ["LOCAL", "CLOUD", "HÍBRIDO"]
