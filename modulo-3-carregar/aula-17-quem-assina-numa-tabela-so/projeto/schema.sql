-- As tabelas do projeto no Postgres. O banco.py roda este arquivo antes de cada carga:
-- IF NOT EXISTS cria só o que falta, então rodar de novo não muda nada.

-- Uma linha por notícia, com as colunas da silver, menos quem assina, que vai para outras tabelas.
-- O id é do banco, e é por ele que as outras tabelas vão apontar para a notícia. O link é a identidade da notícia
-- que vem de fora: UNIQUE recusa o mesmo link duas vezes, venha ele do feed ou do mapa do site.
-- As regras de erro do validar.py viram CHECK; os avisos ficam na coluna avisos, como dado.
CREATE TABLE IF NOT EXISTS noticias (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    link         text NOT NULL UNIQUE CHECK (link LIKE 'https://g1.globo.com/%'),
    dia          date NOT NULL,
    publicado_em timestamptz,
    precisao     text NOT NULL CHECK (precisao IN ('hora', 'dia')),
    editoria     text NOT NULL,
    titulo       text,
    subtitulo    text,
    palavras     integer CHECK (palavras >= 0),
    mesma_que    text REFERENCES noticias (link),
    origem       text NOT NULL CHECK (origem IN ('feed', 'sitemap')),
    visto_em     timestamptz NOT NULL,
    avisos       text,
    carregada_em timestamptz NOT NULL DEFAULT now(),
    mudou_em     timestamptz NOT NULL DEFAULT now(),
    CHECK (publicado_em <= visto_em)
);

-- Quem assina: uma linha por nome, com o tipo da fonte. O tipo é do nome, e não da notícia: mora aqui, uma vez só.
CREATE TABLE IF NOT EXISTS autores (
    id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome text NOT NULL UNIQUE,
    tipo text NOT NULL CHECK (tipo IN ('redação', 'repórter', 'agência', 'publicidade'))
);

-- A assinatura de cada notícia: uma linha por nome, na ordem da linha "Por ...". As duas chaves estrangeiras
-- recusam uma assinatura de notícia ou de nome que não existe, e recusam apagar um nome que ainda assina.
CREATE TABLE IF NOT EXISTS assinaturas (
    noticia_id bigint NOT NULL REFERENCES noticias (id),
    ordem      smallint NOT NULL CHECK (ordem >= 1),
    autor_id   bigint NOT NULL REFERENCES autores (id),
    PRIMARY KEY (noticia_id, ordem)
);
-- A chave (noticia_id, ordem) serve a busca pela notícia. A busca pelo nome ("as notícias da Reuters") pede outro
-- índice: o Postgres não cria índice na coluna que aponta para outra tabela.
CREATE INDEX IF NOT EXISTS assinaturas_autor ON assinaturas (autor_id);

