# Paris Projects

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

## Como usar

### Opção 1: só baixar e usar (recomendado)

Baixe o **`ParisProjects.exe`** na página de [Releases](../../releases) do repositório, coloque numa pasta fixa (por exemplo `Documentos\ParisProjects`) e dê dois cliques. O navegador abre sozinho no app.

- Os seus projetos ficam salvos num arquivo ao lado do `.exe`.
- Para encerrar, feche a janela preta.
- Se o Windows mostrar "O Windows protegeu o computador", clique em **Mais informações → Executar assim mesmo** (o aviso aparece porque o executável não tem assinatura digital).

### Opção 2: gerar o executável a partir do código (Windows)

1. Baixe o código (**Code → Download ZIP**) e **extraia** o zip.
2. Dê dois cliques em **`gerar_exe.bat`**.

O script faz tudo sozinho: confere o Python (e oferece instalar, se não houver), cria o ambiente virtual, instala as dependências, roda os testes e gera o `dist\ParisProjects.exe`. No final, ele pergunta se você quer abrir o programa.

Não é preciso rodar como administrador. Na primeira vez leva alguns minutos, porque baixa as dependências da internet.

### Opção 3: rodar pelo código (desenvolvimento)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

python app.py                   # modo desenvolvimento (recarga automática)
python iniciar.py               # modo de uso (abre o navegador sozinho)
```

Acesse **http://127.0.0.1:5000**. O banco (`implantacoes.db`) é criado automaticamente no primeiro uso.

## Testes

```bash
python testar_regras.py
```

Os testes conferem as regras de prazo com uma data fixa, incluindo feriados e fins de semana. O `gerar_exe.bat` roda esses testes antes de gerar o executável e não gera nada se algum falhar.

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
├── gerar_exe.bat        # prepara tudo e gera o executável
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
