-- Estrutura do banco de dados da Mini Ferramenta de Gestão de Implantações
-- "IF NOT EXISTS" garante que rodar este script de novo NÃO apaga seus dados.

CREATE TABLE IF NOT EXISTS projetos (
    -- Identificação
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente                   TEXT NOT NULL,
    produto                   TEXT NOT NULL CHECK (produto IN ('PACS', 'RIS')),

    -- Links
    infra_url                 TEXT,
    doc_url                   TEXT,

    -- Datas (sempre no formato AAAA-MM-DD)
    data_inicio_projeto       TEXT,
    planilhas_data_envio      TEXT,
    planilhas_data_devolucao  TEXT,
    data_inicio_cadastro      TEXT,
    data_inicio_treinamentos  TEXT,

    -- Etapas com opções fixas
    validacao_cliente         TEXT NOT NULL DEFAULT 'PENDENTE'
        CHECK (validacao_cliente IN ('PENDENTE', 'EM ANDAMENTO', 'CONCLUÍDO')),
    passagem_homologacao      TEXT NOT NULL DEFAULT 'ENVIAR E-MAIL DE PASSAGEM'
        CHECK (passagem_homologacao IN ('ENVIAR E-MAIL DE PASSAGEM', 'ENVIADO E-MAIL DE PASSAGEM')),
    reuniao_implantador       TEXT NOT NULL DEFAULT 'PENDENTE'
        CHECK (reuniao_implantador IN ('PENDENTE', 'CONCLUÍDO')),

    -- Fase escolhida pelo usuário (ATRASADO NÃO fica aqui: é calculado pelo sistema)
    fase                      TEXT NOT NULL DEFAULT 'INÍCIO'
        CHECK (fase IN ('INÍCIO', 'EM ANDAMENTO', 'FINALIZADO')),

    -- Campos secundários
    tipo_projeto              TEXT CHECK (tipo_projeto IN ('AP', 'NR', 'AP+NR')),
    tipo_servidor             TEXT CHECK (tipo_servidor IN ('LOCAL', 'CLOUD', 'HÍBRIDO')),
    gp                        TEXT,
    telelaudo                 TEXT,   -- nome da Tele; vazio = "Não há"
    integracao                TEXT,   -- descrição da integração; vazio = "Não há"

    -- Controle interno
    criado_em                 TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    atualizado_em             TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
