# Movies on My Radar

Backend em Python que acompanha o catálogo nacional da Cinemark e envia avisos sobre filmes em um canal público do Telegram.

## Sobre o projeto

O projeto identifica:

- filmes que estrearão nos próximos 7 dias;
- filmes que passaram a estar em cartaz nacionalmente.

A ideia inicial era utilizar web scraping, mas a investigação mostrou que o site carrega os dados por uma API interna não documentada. Por isso, o projeto consumirá as respostas JSON utilizadas pelo próprio site.

## Como funciona

```text
Catálogo da Cinemark
        ↓
Coleta e deduplicação dos filmes
        ↓
Aplicação das regras de elegibilidade
        ↓
Persistência no SQLite
        ↓
Publicação no Telegram
```

## Tecnologias

- Python 3.12+
- Requests
- SQLite
- python-dotenv
- pytest
- Telegram Bot API

## Status

🚧 Em desenvolvimento — implementação do MVP.

A primeira versão será executada manualmente e utilizará um cache local de cidades e cinemas para realizar a coleta nacional.

## Documentação

- [Planejamento do projeto](PROJECT.md)
- [Decisões do projeto](DECISIONS.md)

## Autor

Desenvolvido por Luis Carlos.
