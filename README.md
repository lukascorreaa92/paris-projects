# Gestão de Implantações

Mini ferramenta web para organizar projetos de implantação de **PACS** e **RIS**: cadastro dos projetos, acompanhamento das etapas e **cálculo automático de prazos e atrasos**.

Roda localmente, no navegador, e cada pessoa tem o seu próprio banco de dados.

## Funcionalidades

- Cadastro e edição de projetos (cliente, produto, links de infra e documentação, datas das etapas, status de validação, homologação e reunião com implantador, além de informações secundárias)
- Cards com cor por status: **Início**, **Em andamento**, **Finalizado** e **Atrasado**
- Status **ATRASADO calculado automaticamente** a partir dos prazos, considerando fins de semana e feriados nacionais
- Tela de detalhe com a data-limite e a situação de cada etapa
- Busca por cliente ou GP (ignora acentos e maiúsculas)
- Filtros por situação e produto, e ordenação por urgência, cliente ou data de início
- Tema claro e escuro
- Executável (`.exe`) para uso no dia a dia, sem precisar instalar Python

## Regras de prazo

| Etapa | Prazo | Concluída quando |
|---|---|---|
| Planilhas | 5 dias **úteis** após o envio | a data de devolução é preenchida |
| Cadastro + treinamentos | 30 dias **corridos** após o início do cadastro | "Validação c/ cliente" = CONCLUÍDO |

O status exibido segue esta ordem: **FINALIZADO** (se a fase for Finalizado) → **ATRASADO** (se alguma etapa estourou o prazo) → a fase escolhida.

As regras ficam em `regras.py`. Os prazos são constantes no topo do arquivo.

## Tecnologias

- Python 3 + [Flask](https://flask.palletsprojects.com/)
- SQLite (banco em arquivo local)
- [holidays](https://pypi.org/project/holidays/) (feriados nacionais)
- HTML, CSS e um pouco de JavaScript (Jinja2 nos templates)
- [PyInstaller](https://pyinstaller.org/) (geração do executável)

## Como rodar (desenvolvimento)

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Rodar
python app.py                  # modo desenvolvimento (recarga automática)
# ou
python iniciar.py              # modo de uso (abre o navegador sozinho)
```

Acesse **http://127.0.0.1:5000**. O banco (`implantacoes.db`) é criado automaticamente no primeiro uso.

## Testes

```bash
python testar_regras.py
```

Os testes conferem as regras de prazo com uma data fixa, incluindo feriados e fins de semana.

## Gerar o executável (Windows)

Com o ambiente virtual ativado, dê dois cliques em `gerar_exe.bat` (ou rode o arquivo no terminal). Não é preciso rodar como administrador.

O executável é gerado em `dist\GestaoImplantacoes.exe`. Coloque-o numa pasta definitiva: o banco de dados e a chave secreta são criados **ao lado do `.exe`**.

## Estrutura

```
├── app.py               # rotas, segurança e filtros de template
├── iniciar.py           # ponto de partida do uso diário / do .exe
├── config.py            # nome do app, porta e chave secreta
├── caminhos.py          # pastas corretas (script ou .exe)
├── database.py          # acesso ao SQLite
├── schema.sql           # estrutura da tabela
├── validacao.py         # validação dos formulários
├── regras.py            # prazos e status
├── filtros.py           # busca, filtros e ordenação
├── opcoes.py            # listas de opções fixas
├── testar_regras.py     # testes das regras de prazo
├── gerar_exe.bat        # gera o executável
├── templates/           # páginas HTML (Jinja2)
└── static/              # CSS, JavaScript e imagens
```

## Segurança e privacidade

- O app escuta **apenas em `127.0.0.1`**: não fica acessível pela rede.
- **O banco de dados não é versionado** (`.gitignore`), porque contém dados reais de clientes.
- A **chave secreta** é gerada aleatoriamente em cada instalação (arquivo `.chave_secreta`, também fora do Git).
- Formulários protegidos contra **CSRF** (token por sessão + cookie `SameSite=Lax`).
- Acesso só pelos hosts `127.0.0.1` e `localhost` (proteção contra *DNS rebinding*).
- Consultas SQL parametrizadas, HTML escapado automaticamente e links aceitos só com `http://` ou `https://`.
