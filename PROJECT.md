# Movies on my radar — PROJECT.md

## 1. Identidade do projeto

O **Movies on my radar** é um serviço backend em Python que monitora o catálogo público da Cinemark, identifica novidades relevantes e publica avisos em um canal público do Telegram.

O projeto nasceu como uma ideia de web scraping, mas a investigação técnica mostrou que os dados úteis não estavam disponíveis nos cards do HTML inicial. O site consulta uma API interna do tipo **BFF — Backend for Frontend** e monta a interface a partir das respostas JSON.

Por isso, a implementação principal será um **consumidor de API interna não documentada**, e não um scraper tradicional de HTML.

A proposta de valor é:

> Pessoas interessadas em cinema podem receber, em um único canal, avisos sobre filmes que estrearão na próxima semana e sobre títulos que passaram a estar em cartaz nacionalmente, sem consultar repetidamente diferentes cinemas e cidades.

---

## 2. Público-alvo

O público-alvo são pessoas interessadas em cinema que desejam acompanhar lançamentos de maneira simples e centralizada.

O Telegram será utilizado como um canal público de distribuição. Todos os inscritos receberão as mesmas publicações.

O MVP não terá:

- cadastro;
- login;
- autenticação;
- preferências individuais;
- cidade favorita por inscrito;
- cinema favorito por inscrito;
- listas pessoais de filmes;
- notificações diferentes por pessoa;
- armazenamento de dados dos inscritos;
- interação individual com o bot.

---

## 3. Objetivo do MVP

O MVP deverá provar o fluxo completo:

```text
coletar catálogo
        ↓
deduplicar filmes
        ↓
salvar o que foi observado
        ↓
avaliar elegibilidade
        ↓
publicar no Telegram
        ↓
registrar somente a publicação confirmada
```

A primeira versão será executada manualmente e utilizará um cache nacional de cidades e cinemas já produzido durante a prova de conceito.

O objetivo não é construir imediatamente uma plataforma completa, mas entregar uma versão pequena, demonstrável, testada e com valor real para portfólio.

---

## 4. Natureza e risco da fonte

Base observada durante a prova de conceito:

```text
https://br-www-frontend-ext-prod.cinemark.com.br/bff-api/v1
```

Essa fonte:

- é utilizada pelo site público da Cinemark;
- retorna JSON estruturado;
- não foi identificada como uma API pública oficialmente documentada;
- pode mudar de endereço, parâmetros, campos ou comportamento sem aviso;
- pode aplicar proteções diferentes conforme o endpoint, o IP ou o ambiente.

A aplicação deverá:

- reutilizar uma `requests.Session`;
- aplicar timeout;
- validar status HTTP;
- validar `Content-Type`;
- validar o campo `success` e a estrutura esperada;
- usar intervalo moderado entre requisições;
- reconhecer respostas HTML inesperadas e possíveis páginas da Cloudflare;
- interromper a coleta quando houver bloqueio, sem insistência agressiva;
- não tentar contornar autenticação, desafios ou mecanismos de proteção.

---

## 5. Evidências técnicas atuais

A investigação já confirmou:

```text
A página principal responde por HTTP
✅

Os cards úteis não estavam disponíveis no HTML inicial
✅

A BFF JSON usada pelo site foi identificada
✅

/movies/onDisplayByTheater retorna JSON
✅

/movies/commingSoon retorna JSON
✅

/movies/detailBySlug retorna JSON
✅
```

Em uma verificação realizada em **14 de julho de 2026**, os três endpoints de filmes continuavam respondendo com JSON e `success: true`.

Os experimentos anteriores também mostraram que os endpoints de localização podiam exigir um conjunto mais completo de cabeçalhos semelhantes aos do navegador.

Para impedir que essa parte aumente o MVP, a atualização automática de localizações foi retirada da primeira entrega.

---

## 6. Delimitação do MVP atual

### 6.1 Incluído no MVP

O MVP incluirá:

- Python 3.12 ou superior;
- consumo dos endpoints de filmes da BFF da Cinemark;
- cache local previamente gerado com cidades, cinemas e estados;
- coleta nacional de filmes em cartaz;
- coleta nacional de filmes em breve;
- deduplicação por ID da Cinemark;
- regra nacional para filmes em cartaz;
- regra por data para filmes em breve;
- consulta de detalhes por slug;
- SQLite local;
- separação entre filme conhecido, observação e publicação confirmada;
- Telegram com pôster e legenda;
- fallback para mensagem de texto;
- execução manual;
- resumo da execução;
- testes automatizados das regras principais.

### 6.2 Primeira atualização após o MVP

Ficarão para a primeira atualização:

- `refresh_locations.py`;
- descoberta automática de estados;
- descoberta automática de cidades;
- descoberta automática de cinemas;
- teste e redução do conjunto de cabeçalhos dos endpoints de localização;
- atualização automática do cache;
- checkpoints e retomada de coleta;
- classificação detalhada em `amplo`, `regional` e `limitado`;
- histórico completo de variação de cobertura;
- avisos de alteração ou adiamento da data de estreia.

### 6.3 Evoluções posteriores

Ficarão para versões posteriores:

- execução agendada;
- hospedagem;
- Docker;
- PostgreSQL;
- painel administrativo;
- múltiplos canais;
- WhatsApp;
- múltiplas redes de cinema;
- usuários e preferências;
- inteligência artificial;
- recomendações personalizadas.

---

## 7. Cache nacional de localizações

O MVP receberá um arquivo local, por exemplo:

```text
data/cinemark-locations.json
```

Esse arquivo será uma fotografia produzida durante a prova de conceito e deverá conter pelo menos:

- estados conhecidos;
- cidades e seus `city_id`;
- cinemas e seus `theater_id`;
- cidade e estado associados a cada cinema;
- data em que o cache foi gerado.

A execução principal não chamará `/states`, `/cities` e `/theaters` no MVP.

Se o cache estiver ausente, vazio ou inválido, o programa deverá interromper com uma mensagem clara.

A desatualização do cache é uma limitação conhecida do MVP. A atualização automática será adicionada depois que o fluxo principal estiver concluído.

---

## 8. Endpoints utilizados no MVP

### 8.1 Filmes em cartaz por cinema

```http
GET /movies/onDisplayByTheater
```

Parâmetros:

```text
theaterId
pageNumber
pageSize
```

O endpoint será consultado para cada cinema único presente no cache.

### 8.2 Filmes em breve por cidade

```http
GET /movies/commingSoon
```

A palavra `comming` possui dois `m` no endpoint observado e deverá ser utilizada exatamente assim.

Parâmetros:

```text
cityId
pageNumber
pageSize
```

O endpoint será consultado para cada cidade única presente no cache.

### 8.3 Detalhes por slug

```http
GET /movies/detailBySlug
```

Parâmetro:

```text
slug
```

Esse endpoint poderá fornecer:

- título;
- sinopse;
- data de estreia;
- distribuidora;
- duração;
- classificação;
- gênero;
- trailer;
- pôsteres;
- direção e elenco, quando cadastrados.

---

## 9. Identidade e deduplicação

### 9.1 Filmes

O identificador principal será o ID fornecido pela Cinemark:

```text
cinemark_id
```

Valores numéricos recebidos como inteiro, string numérica ou número integral deverão ser normalizados para um inteiro positivo.

Exemplos aceitos:

```python
9129
"9129"
9129.0
```

Título e slug não serão usados como identidade principal.

### 9.2 Publicações

A regra de unicidade será:

```text
UNIQUE(cinemark_id, category)
```

Categorias:

```text
em_breve
em_cartaz
```

Isso permite que o mesmo filme seja publicado uma vez antes da estreia e outra vez quando entrar em cartaz nacionalmente.

---

## 10. Fluxo de filmes em cartaz

```text
Carregar cinemas do cache
        ↓
Consultar onDisplayByTheater para cada cinema
        ↓
Validar paginação e resposta
        ↓
Deduplicar por cinemark_id
        ↓
Registrar os cinemas e estados onde cada filme apareceu
        ↓
Calcular cobertura por cinema e estado
        ↓
Salvar filme e observação
        ↓
Avaliar filtro nacional
        ↓
Verificar se já existe publication em_cartaz
        ↓
Consultar detalhes do candidato novo
        ↓
Enviar ao Telegram
        ↓
Registrar publication somente após confirmação
```

---

## 11. Regra nacional para filmes em cartaz

A cobertura por cinema será:

```python
theater_coverage = movie_theater_count / processed_theater_count
```

A cobertura por estado será:

```python
state_coverage = movie_state_count / processed_state_count
```

O denominador deverá usar somente os cinemas e estados processados com sucesso na execução atual.

Um filme será elegível como nacional quando:

```text
cobertura de cinemas >= 80%
e
cobertura de estados >= 80%
```

Os limites serão configuráveis:

```env
NATIONAL_THEATER_COVERAGE_THRESHOLD=0.80
NATIONAL_STATE_COVERAGE_THRESHOLD=0.80
```

Filmes abaixo do limite:

- serão salvos;
- terão sua observação atualizada;
- não serão marcados como publicados;
- serão recalculados nas execuções seguintes;
- poderão ser publicados quando cruzarem o limite.

O MVP não precisa classificá-los em amplo, regional ou limitado. Ele precisa apenas saber se o filme é ou não elegível como nacional.

---

## 12. Fluxo de filmes em breve

A categoria `em_breve` será controlada pela data de estreia, e não por percentual de cobertura.

```text
Carregar cidades do cache
        ↓
Consultar commingSoon para cada cidade
        ↓
Deduplicar por cinemark_id
        ↓
Salvar dados básicos
        ↓
Obter ou atualizar detalhes para conhecer release_date
        ↓
Calcular dias até a estreia
        ↓
Salvar filme e observação
        ↓
Está entre 0 e 7 dias da estreia?
    não → continuar observando
    sim → verificar publication em_breve
                ↓
          ainda não publicou?
                ↓
          enviar mensagem de estreia próxima
                ↓
          registrar publication após confirmação
```

### 12.1 Janela de publicação

A janela será inclusiva:

```text
0 <= dias_ate_estreia <= 7
```

Exemplos:

```text
Faltam 7 dias → elegível
Faltam 4 dias → elegível
Estreia hoje → elegível
A estreia já passou → não publicar como em_breve
```

Como a execução será manual, o programa enviará a mensagem na primeira execução realizada dentro dessa janela.

### 12.2 Dados obrigatórios

Para uma publicação `em_breve`, serão obrigatórios:

- `cinemark_id` válido;
- título;
- slug;
- `release_date` válida.

Um filme sem data válida poderá ser salvo, mas não será elegível para a mensagem de uma semana antes.

### 12.3 Alteração de data

Depois que o filme tiver sido publicado como `em_breve`, uma mudança posterior na data atualizará o banco, mas não produzirá automaticamente outra mensagem no MVP.

Avisos de adiamento ou antecipação serão uma evolução futura.

---

## 13. Consequência técnica da regra de sete dias

A listagem de `commingSoon` observada não fornece necessariamente a data de estreia.

Por isso, o sistema poderá precisar consultar `detailBySlug` para cada filme em breve único que ainda não tenha uma data válida ou cuja data precise ser atualizada.

Essa categoria possui uma otimização diferente de `em_cartaz`:

```text
EM CARTAZ
filtrar por cobertura antes de consultar detalhes

EM BREVE
consultar detalhes para conhecer a data
antes de avaliar a janela de sete dias
```

Para reduzir requisições, detalhes já salvos poderão ser reutilizados durante a mesma execução e atualizados de acordo com uma política simples de recência.

No primeiro MVP, é aceitável atualizar os detalhes dos filmes em breve em cada execução manual, desde que o volume permaneça moderado e o intervalo entre requisições seja respeitado.

---

## 14. Persistência

O banco será SQLite.

A existência de um filme no banco não significa que uma mensagem foi publicada.

### 14.1 Tabela `movies`

Guarda a identidade e os detalhes conhecidos do filme.

```sql
CREATE TABLE movies (
    cinemark_id INTEGER PRIMARY KEY,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    synopsis TEXT,
    release_date TEXT,
    distributor TEXT,
    runtime INTEGER,
    age_indication TEXT,
    rating_description TEXT,
    genre TEXT,
    trailer_url TEXT,
    poster_url TEXT,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### 14.2 Tabela `movie_observations`

Guarda o estado mais recente observado em cada categoria.

```sql
CREATE TABLE movie_observations (
    cinemark_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    location_count INTEGER,
    state_count INTEGER,
    location_coverage REAL,
    state_coverage REAL,
    is_eligible INTEGER NOT NULL,
    observed_at TEXT NOT NULL,

    PRIMARY KEY (cinemark_id, category),

    FOREIGN KEY (cinemark_id)
        REFERENCES movies(cinemark_id)
);
```

Em `em_cartaz`, os campos de cobertura serão preenchidos.

Em `em_breve`, a elegibilidade será determinada pela data de estreia e os campos de cobertura poderão ser nulos.

### 14.3 Tabela `publications`

Guarda somente mensagens confirmadas pelo Telegram.

```sql
CREATE TABLE publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cinemark_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    telegram_message_id TEXT,
    delivery_type TEXT NOT NULL,
    published_at TEXT NOT NULL,

    FOREIGN KEY (cinemark_id)
        REFERENCES movies(cinemark_id),

    UNIQUE (cinemark_id, category)
);
```

Valores de `delivery_type`:

```text
photo
text_fallback
```

---

## 15. Ordem entre SQLite e Telegram

A ordem correta será:

```text
Coletar e deduplicar
        ↓
Salvar ou atualizar movies
        ↓
Salvar ou atualizar movie_observations
        ↓
Avaliar elegibilidade
        ↓
Verificar publications
        ↓
Tentar Telegram
        ↓
Telegram confirmou?
    não → não criar publication
    sim → criar publication
```

Salvar o filme antes do Telegram não significa marcá-lo como publicado.

A tabela `publications` será a única fonte de verdade para saber se a mensagem foi entregue.

Se o Telegram falhar:

- o filme continua conhecido;
- a observação continua salva;
- a publicação continua ausente;
- uma nova tentativa poderá ocorrer na próxima execução.

Existe uma pequena janela em que o Telegram pode aceitar a mensagem e o programa falhar antes de inserir `publications`. Essa situação pode gerar uma duplicidade na próxima execução e será aceita como limitação do MVP.

---

## 16. Primeira execução

A primeira execução não será silenciosa.

### `em_cartaz`

Serão publicados todos os filmes que:

1. forem deduplicados;
2. tiverem dados mínimos válidos;
3. passarem pelos dois limites de 80%;
4. ainda não tiverem `publication` em `em_cartaz`;
5. tiverem seus detalhes obtidos;
6. forem confirmados pelo Telegram.

### `em_breve`

Serão publicados todos os filmes que:

1. tiverem dados mínimos válidos;
2. tiverem data de estreia válida;
3. estiverem entre zero e sete dias da estreia;
4. ainda não tiverem `publication` em `em_breve`;
5. forem confirmados pelo Telegram.

---

## 17. Publicação no Telegram

A forma principal será:

```text
pôster + legenda
```

A aplicação utilizará `sendPhoto` quando houver uma URL HTTPS válida.

Ordem de preferência do pôster:

```text
1. desktop_poster_image
2. mobile_poster_image
3. tablet_poster_image
```

Se não existir pôster válido ou `sendPhoto` falhar, a aplicação tentará `sendMessage`.

```text
sendPhoto funcionou
→ delivery_type = photo

sendPhoto falhou e sendMessage funcionou
→ delivery_type = text_fallback

ambos falharam
→ não criar publication
```

---

## 18. Formato das mensagens

### 18.1 Filme em breve

Exemplo:

```text
🎬 ESTREIA NESTA SEMANA

Nome do filme

📅 Estreia: 21/07/2026
⏳ Faltam 7 dias
🎭 Gênero: ...
🔞 Classificação: ...
⏱ Duração: ...

📝 Sinopse:
...

🎞 Trailer:
https://...

🔗 Cinemark:
https://www.cinemark.com.br/filme/<slug>
```

O texto do contador poderá variar:

```text
Estreia hoje
Falta 1 dia
Faltam 4 dias
Estreia daqui a 1 semana
```

### 18.2 Filme em cartaz

Exemplo:

```text
🍿 AGORA EM CARTAZ NACIONALMENTE

Nome do filme

🌎 Presença: 84 de 85 cinemas monitorados
🎭 Gênero: ...
🔞 Classificação: ...
⏱ Duração: ...

📝 Sinopse:
...

🎞 Trailer:
https://...

🔗 Cinemark:
https://www.cinemark.com.br/filme/<slug>
```

A exibição da cobertura na mensagem poderá ser configurável, mas o cálculo será obrigatório.

---

## 19. Limite da legenda

A aplicação adotará:

```python
TELEGRAM_CAPTION_LIMIT = 1000
```

Prioridades:

1. categoria;
2. título;
3. data ou informação de distribuição;
4. dados principais;
5. trailer;
6. link da Cinemark;
7. sinopse dentro do espaço restante.

Se o conteúdo ultrapassar o limite:

- apenas a sinopse será reduzida;
- URLs não serão cortadas;
- serão adicionadas reticências;
- o primeiro MVP usará texto simples, sem `parse_mode`.

---

## 20. Campos ausentes

Valores como estes são válidos:

```json
{
  "runtime": 0,
  "ageIndication": null,
  "director": null,
  "cast": null,
  "trailerUrl": null,
  "assets": []
}
```

A mensagem não deverá exibir `None`, `null` ou duração igual a zero como se fossem dados reais.

Campos opcionais ausentes serão omitidos.

A ausência do pôster provocará fallback de texto.

A ausência de trailer, classificação, direção ou elenco não impedirá a publicação.

A ausência de `release_date` impedirá apenas a publicação `em_breve` baseada na janela de sete dias.

---

## 21. Cabeçalhos HTTP no MVP

Os endpoints de filmes serão chamados inicialmente com o menor conjunto razoável:

```python
HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Origin": "https://www.cinemark.com.br",
    "Referer": "https://www.cinemark.com.br/",
    "User-Agent": "<user-agent centralizado e configurável>",
}
```

O código não deverá copiar permanentemente todos os cabeçalhos `sec-ch-*` de uma versão específica do Chrome sem evidência de necessidade.

Como os endpoints de localização foram retirados do MVP, o conjunto mais sensível de cabeçalhos não bloqueia a primeira entrega.

Antes da atualização que implementar `refresh_locations.py`, deverá ser executado o experimento de redução de cabeçalhos descrito no `decisoes.md`.

---

## 22. Paginação

Os clientes de listagem deverão respeitar:

```text
pageNumber
totalPages
hasNextPage
```

Enquanto `hasNextPage` for verdadeiro, a página seguinte deverá ser consultada.

Um `pageSize` alto não elimina a necessidade de implementar a regra de paginação.

---

## 23. Controle de ritmo e bloqueio

Configuração inicial:

```env
CINEMARK_TIMEOUT_SECONDS=20
CINEMARK_REQUEST_DELAY_SECONDS=1.5
CINEMARK_PAGE_SIZE=999
```

O programa deverá reconhecer um possível bloqueio quando houver combinação como:

```text
HTTP 403
Content-Type: text/html
conteúdo contendo Cloudflare ou Attention Required
```

Ao detectar bloqueio:

- interromper a categoria atual;
- não insistir agressivamente;
- preservar o que já estiver salvo;
- informar claramente no resumo;
- retornar código de saída específico.

Checkpoints detalhados e retomada automática ficam fora do MVP.

---

## 24. Estrutura sugerida

```text
movies-on-my-radar/
├── main.py
├── config.py
├── cinemark_client.py
├── location_cache.py
├── national_catalog.py
├── eligibility.py
├── database.py
├── telegram_client.py
├── message_formatter.py
├── asset_selector.py
├── models.py
├── exceptions.py
├── requirements.txt
├── .env.example
├── README.md
├── PROJECT.md
├── decisoes.md
├── data/
│   ├── .gitkeep
│   └── cinemark-locations.json
├── experiments/
│   ├── teste_cinemark.py
│   ├── teste_api_cinemark.py
│   ├── teste_catalogo_nacional_em_cartaz.py
│   ├── teste_em_breve.py
│   ├── teste_detalhes.py
│   └── teste_headers_minimos.py
└── tests/
    ├── test_id_normalization.py
    ├── test_movie_deduplication.py
    ├── test_eligibility_on_display.py
    ├── test_eligibility_coming_soon.py
    ├── test_pagination.py
    ├── test_persistence.py
    ├── test_message_formatter.py
    └── test_asset_selector.py
```

`teste_headers_minimos.py` será necessário somente antes da atualização de descoberta automática de localizações.

---

## 25. Configuração

Exemplo:

```env
CINEMARK_API_BASE_URL=https://br-www-frontend-ext-prod.cinemark.com.br/bff-api/v1
CINEMARK_TIMEOUT_SECONDS=20
CINEMARK_REQUEST_DELAY_SECONDS=1.5
CINEMARK_PAGE_SIZE=999
CINEMARK_LOCATIONS_CACHE_PATH=data/cinemark-locations.json

NATIONAL_THEATER_COVERAGE_THRESHOLD=0.80
NATIONAL_STATE_COVERAGE_THRESHOLD=0.80
COMING_SOON_WINDOW_DAYS=7

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_CAPTION_LIMIT=1000

DATABASE_PATH=data/movies-on-my-radar.db
```

O `.env` real não será enviado ao GitHub.

---

## 26. Testes automatizados mínimos

O MVP deverá testar:

- normalização de ID inteiro e string;
- deduplicação de filmes encontrados em vários cinemas;
- deduplicação de filmes encontrados em várias cidades;
- paginação;
- cobertura por cinema;
- cobertura por estado;
- limite nacional de 80%;
- janela de `em_breve` em 7, 1 e 0 dias;
- filme com estreia já passada;
- filme sem data de estreia;
- primeira execução com candidatos elegíveis;
- filme salvo sem publicação;
- falha no Telegram sem criação de `publication`;
- publicação confirmada com chave única;
- seleção de pôster;
- fallback de texto;
- truncamento da sinopse;
- campos opcionais ausentes.

Os testes de regra não deverão depender da internet.

---

## 27. Execução

```bash
python main.py
```

O comando deverá:

1. carregar configuração;
2. abrir o SQLite;
3. carregar e validar o cache de localizações;
4. coletar `em_cartaz` por cinema;
5. coletar `em_breve` por cidade;
6. validar paginação e respostas;
7. deduplicar filmes;
8. salvar filmes e observações;
9. calcular elegibilidade de cada categoria;
10. consultar detalhes necessários;
11. ignorar publicações já registradas;
12. selecionar pôster;
13. formatar mensagem;
14. tentar `sendPhoto`;
15. usar `sendMessage` como fallback;
16. registrar somente entregas confirmadas;
17. exibir resumo final.

---

## 28. Resumo esperado

Exemplo:

```text
Execução concluída.

Cinemas carregados do cache: 85
Cinemas processados: 85
Filmes únicos em cartaz: 22
Filmes nacionais elegíveis: 5

Cidades carregadas do cache: 48
Cidades processadas: 48
Filmes únicos em breve: 18
Filmes dentro da janela de 7 dias: 2

Filmes salvos ou atualizados: 35
Publicações já conhecidas: 5
Novas publicações enviadas: 2
Publicações com foto: 2
Fallbacks em texto: 0
Falhas de publicação: 0
Bloqueio detectado: não
```

---

## 29. Códigos de saída sugeridos

```text
0 → execução concluída sem falhas
2 → configuração inválida
3 → falha geral ao consultar a Cinemark
4 → resposta incompatível
5 → falha geral no banco
6 → execução parcial com falhas
7 → coleta interrompida por bloqueio
8 → cache ausente ou inválido
```

---

## 30. Condições de sucesso do MVP

O MVP estará concluído quando:

- o cache local for carregado e validado;
- a coleta nacional em cartaz funcionar;
- a cobertura nacional for calculada corretamente;
- filmes nacionais novos forem publicados uma única vez;
- a coleta nacional de `em_breve` funcionar;
- filmes dentro da janela de sete dias forem publicados uma única vez;
- filmes e observações forem salvos antes da tentativa de entrega;
- somente envios confirmados criarem registros em `publications`;
- o pôster funcionar com fallback de texto;
- os testes críticos estiverem verdes;
- a execução manual apresentar um resumo compreensível;
- o projeto não depender de scraping HTML, Selenium ou Playwright.

---

## 31. Arquitetura consolidada

```text
CACHE LOCAL DE LOCALIZAÇÕES
cidades + cinemas + estados
        ↓
MAIN
        ↓
┌────────────────────────────────────────────┐
│ EM CARTAZ                                  │
│ cinemas → listagens → deduplicação         │
│ → cobertura 80%/80% → elegibilidade        │
└────────────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ EM BREVE                                   │
│ cidades → listagens → deduplicação         │
│ → detalhes/data → janela de 7 dias         │
└────────────────────────────────────────────┘
        ↓
SALVAR MOVIES E OBSERVATIONS
        ↓
VERIFICAR PUBLICATIONS
        ↓
DETALHES, PÔSTER E FORMATAÇÃO
        ↓
TELEGRAM SENDPHOTO
        ↓
FALLBACK SENDMESSAGE
        ↓
CONFIRMAÇÃO
        ↓
CRIAR PUBLICATION
```

---

## 32. Classificação final do projeto

O Movies on my radar não será descrito como um scraper tradicional em sua implementação principal.

A descrição técnica correta será:

> Backend em Python que consome uma API interna não documentada utilizada pelo site da Cinemark, agrega o catálogo nacional, aplica regras de elegibilidade, persiste observações em SQLite e publica novidades no Telegram.

A investigação inicial de scraping continuará documentada porque ela explica como a API foi descoberta e demonstra o processo real de engenharia.
