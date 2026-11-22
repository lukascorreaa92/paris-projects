from datetime import date

import opcoes

# Nomes "amigáveis" de cada campo, usados nas mensagens de erro
ROTULOS = {
    "cliente": "Cliente",
    "produto": "Produto",
    "infra_url": "Infra",
    "doc_url": "Doc",
    "data_inicio_projeto": "Data início do projeto",
    "planilhas_data_envio": "Planilhas: data de envio",
    "planilhas_data_devolucao": "Planilhas: data de devolução",
    "data_inicio_cadastro": "Data início do cadastro",
    "data_inicio_treinamentos": "Data início dos treinamentos",
    "validacao_cliente": "Validação c/ cliente",
    "passagem_homologacao": "Passagem p/ homologação",
    "reuniao_implantador": "Reunião c/ implantador",
    "fase": "Fase do projeto",
    "tipo_projeto": "Tipo de projeto",
    "tipo_servidor": "Tipo de servidor",
    "gp": "GP",
    "telelaudo": "Telelaudo",
    "integracao": "Integração",
}

# Agrupamos os campos pelo TIPO de validação que cada um precisa
CAMPOS_TEXTO = ["cliente", "gp", "telelaudo", "integracao"]
CAMPOS_URL = ["infra_url", "doc_url"]
CAMPOS_DATA = [
    "data_inicio_projeto",
    "planilhas_data_envio",
    "planilhas_data_devolucao",
    "data_inicio_cadastro",
    "data_inicio_treinamentos",
]
CAMPOS_OPCAO = {
    "produto": opcoes.PRODUTOS,
    "fase": opcoes.FASES,
    "validacao_cliente": opcoes.VALIDACAO_CLIENTE,
    "passagem_homologacao": opcoes.PASSAGEM_HOMOLOGACAO,
    "reuniao_implantador": opcoes.REUNIAO_IMPLANTADOR,
    "tipo_projeto": opcoes.TIPOS_PROJETO,
    "tipo_servidor": opcoes.TIPOS_SERVIDOR,
}
OBRIGATORIOS = [
    "cliente",
    "produto",
    "fase",
    "validacao_cliente",
    "passagem_homologacao",
    "reuniao_implantador",
]


def validar_projeto(form):
    """Limpa e confere os dados do formulário.

    Devolve (dados, erros):
      - dados: dicionário pronto para gravar no banco
      - erros: lista de mensagens; vazia significa que está tudo certo
    """
    dados = {}
    erros = []

    # 1) Limpeza: tira espaços das pontas; campo vazio vira None (NULL no banco)
    todos_os_campos = CAMPOS_TEXTO + CAMPOS_URL + CAMPOS_DATA + list(CAMPOS_OPCAO)
    for campo in todos_os_campos:
        valor = form.get(campo, "").strip()
        dados[campo] = valor if valor else None

    # 2) Campos obrigatórios
    for campo in OBRIGATORIOS:
        if dados[campo] is None:
            erros.append(f"O campo '{ROTULOS[campo]}' é obrigatório.")

    # 3) Listas de opção: o valor precisa estar na lista permitida
    for campo, permitidos in CAMPOS_OPCAO.items():
        valor = dados[campo]
        if valor is not None and valor not in permitidos:
            erros.append(f"Valor inválido em '{ROTULOS[campo]}'.")

    # 4) Links precisam começar com http:// ou https://
    for campo in CAMPOS_URL:
        valor = dados[campo]
        if valor and not valor.startswith(("http://", "https://")):
            erros.append(f"'{ROTULOS[campo]}' precisa ser um link começando com http:// ou https://")

    # 5) Datas precisam estar no formato AAAA-MM-DD e ser datas reais
    for campo in CAMPOS_DATA:
        valor = dados[campo]
        if valor:
            try:
                date.fromisoformat(valor)
            except ValueError:
                erros.append(f"'{ROTULOS[campo]}' não é uma data válida.")
                dados[campo] = None  # evita comparar data inválida no passo 6

    # 6) Regra de negócio: a devolução não pode ser antes do envio
    envio = dados["planilhas_data_envio"]
    devolucao = dados["planilhas_data_devolucao"]
    if envio and devolucao and devolucao < envio:
        erros.append("A devolução das planilhas não pode ser anterior ao envio.")

    return dados, erros
