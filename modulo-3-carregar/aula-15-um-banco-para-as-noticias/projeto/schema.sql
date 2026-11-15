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

