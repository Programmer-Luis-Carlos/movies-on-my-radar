# Movies on my radar — registro consolidado de decisões

## 1. Objetivo

Este documento registra como o Movies on my radar evoluiu, quais alternativas foram consideradas, quais decisões são válidas no MVP atual e quais funcionalidades foram adiadas.

O `PROJECT.md` define como o sistema deverá funcionar.

Este arquivo explica por que essas regras foram escolhidas.

---

## 2. Contexto inicial

A ideia original era criar um projeto de portfólio voltado a backend que monitorasse uma página de cinema e enviasse uma mensagem quando surgisse um filme novo.

O fluxo imaginado era:

```text
HTML da página
        ↓
BeautifulSoup
        ↓
filmes extraídos
        ↓
SQLite
        ↓
Telegram
```

O objetivo educacional era praticar:

- requisições HTTP;
- coleta de dados;
- banco de dados;
- integração com API;
- regras de deduplicação;
- tratamento de erros;
- testes;
- documentação.

---

# Parte I — Produto

## 3. Usar um canal público do Telegram

### Decisão

O sistema publicará em um único canal público do Telegram.

### Motivo

Todos os inscritos podem receber a mesma informação. Não existe necessidade real de cadastro ou personalização no primeiro produto.

### Consequências

Ficam fora do MVP:

- usuários;
- login;
- preferências individuais;
- cidade e cinema favoritos;
- notificações personalizadas;
- bot conversacional.

### Situação

**Confirmada.**

---

## 4. Usar Telegram antes de WhatsApp

### Decisão

A primeira entrega utilizará a Telegram Bot API.

### Motivo

O Telegram permite integrar `sendPhoto` e `sendMessage` por HTTP com menos configuração e sem adicionar uma segunda plataforma antes que o fluxo principal esteja estável.

### Situação

**Confirmada.**

WhatsApp permanece fora do MVP.

---

## 5. Monitorar dois momentos diferentes

### Decisão

O projeto terá duas categorias:

```text
em_breve
em_cartaz
```

### Motivo

São eventos diferentes para o público:

- o filme está próximo da estreia;
- o filme já entrou em cartaz com distribuição nacional.

### Regra

```text
UNIQUE(cinemark_id, category)
```

O mesmo filme pode ser publicado uma vez em cada categoria.

### Situação

**Confirmada.**

---

# Parte II — Da ideia de scraping ao consumo de API

## 6. Testar primeiro o HTML público

### Teste

A página principal respondeu ao `requests` com HTML, mas os cards úteis e links dos filmes não estavam presentes de forma adequada na resposta inicial.

### Conclusão

O conteúdo era carregado por JavaScript a partir de chamadas internas.

### Situação

**Investigação concluída.**

---

## 7. Descartar BeautifulSoup como fonte principal

### Alternativas consideradas

- BeautifulSoup;
- Selenium;
- Playwright;
- consumir os endpoints JSON usados pelo site.

### Decisão

Consumir os endpoints JSON da BFF utilizada pela própria página.

### Motivo

A resposta JSON é mais estruturada e exige menos processamento do que abrir um navegador e interpretar a interface.

### Consequência conceitual

O projeto deixou de ser um scraper tradicional de HTML.

A descrição técnica correta passou a ser:

> Consumidor de uma API interna não documentada descoberta durante a investigação do site.

A etapa de scraping ainda faz parte da história do projeto porque foi a hipótese inicial que levou à descoberta da BFF.

### Situação

**Confirmada.**

---

## 8. Tratar a BFF como fonte não oficial

### Decisão

A aplicação tratará a BFF como uma fonte interna, não documentada e sujeita a alterações.

### Consequências

O cliente deverá:

- validar respostas;
- usar timeout;
- usar ritmo moderado;
- reconhecer HTML inesperado;
- interromper quando houver bloqueio;
- não tentar contornar proteção ou autenticação.

### Situação

**Confirmada.**

---

# Parte III — Investigação nacional

## 9. Não depender da localização física

### Problema inicial

Havia dúvida sobre a possibilidade de o site escolher cidade e cinema por localização, IP, cookie ou GPS.

### Descoberta

Os endpoints recebem `stateId`, `cityId` e `theaterId` explicitamente.

### Decisão

A lógica não dependerá de GPS, cookies de preferência, janela anônima, VPN ou localização física do computador.

### Situação

**Confirmada.**

---

## 10. Descobrir estados, cidades e cinemas

### Prova de conceito

A investigação percorreu estados, cidades e cinemas, deduplicando os cinemas pelo campo `code`.

Resultados observados durante a prova:

```text
15 estados
48 cidades
365 ocorrências de cinemas
85 cinemas únicos
```

Esses valores representam uma fotografia da fonte e não serão codificados como constantes permanentes.

### Situação

**Validada tecnicamente.**

---

## 11. Consultar nacionalmente os filmes em cartaz

### Problema

Um único cinema retornou apenas parte do catálogo.

### Prova de conceito

Em uma fotografia da fonte:

```text
85 cinemas processados
616 ocorrências de filmes
22 filmes únicos
```

### Decisão

A aplicação deverá consultar todos os cinemas conhecidos e deduplicar por `cinemark_id`.

### Situação

**Confirmada.**

---

## 12. Usar o ID da Cinemark

### Decisão

O identificador principal será:

```text
cinemark_id
```

### Alternativa anterior

SHA-256 da URL normalizada.

### Motivo da mudança

O ID da fonte é mais adequado que título, slug ou URL para representar a identidade do filme.

### Situação

**Confirmada.**

---

## 13. Normalizar IDs externos

### Problema encontrado

Uma validação que aceitava somente `int` descartou IDs recebidos como strings numéricas.

### Decisão

Aceitar e normalizar:

```python
9129
"9129"
9129.0
```

### Aprendizado

HTTP 200 não garante que a transformação interna esteja correta. Métricas inconsistentes precisam ser tratadas como sinal de erro.

### Situação

**Confirmada.**

---

# Parte IV — Escopo e tamanho do projeto

## 14. Reconhecer que o projeto cresceu

### Avaliação

A primeira ideia era pequena:

```text
uma página
→ detectar filme novo
→ Telegram
```

Depois da investigação, o projeto passou a envolver:

- API interna;
- dezenas de cidades e cinemas;
- agregação nacional;
- deduplicação;
- cobertura geográfica;
- duas categorias;
- datas de estreia;
- SQLite com responsabilidades separadas;
- pôster e fallback;
- Cloudflare;
- cache de localizações;
- testes e observabilidade.

Para um primeiro projeto backend, implementar tudo de uma vez aumentaria o risco de abandono e dificultaria aprender cada etapa.

### Decisão

Dividir o produto em entregas.

### Situação

**Confirmada.**

---

## 15. Manter o monitoramento nacional no MVP

### Decisão

A coleta nacional continuará no MVP porque ela é a principal característica que diferencia o projeto de um monitor de um único cinema.

### Motivo

A prova de conceito mostrou que um cinema fixo não representa o catálogo da rede.

### Situação

**Confirmada.**

---

## 16. Retirar a atualização automática de localizações do MVP

### Decisão

O MVP utilizará um cache local de cidades, cinemas e estados gerado durante a prova de conceito.

A execução principal não chamará:

```text
/states
/cities
/theaters
```

### Motivos

Essa mudança:

- reduz três etapas de coleta;
- retira do caminho crítico os endpoints mais sensíveis à Cloudflare;
- evita finalizar agora o perfil completo de cabeçalhos;
- mantém a coleta nacional de filmes;
- permite concentrar o aprendizado no fluxo principal.

### Limitação aceita

O cache poderá ficar desatualizado até ser regenerado manualmente.

### Evolução

A primeira atualização após o MVP adicionará `refresh_locations.py` e atualização automática do cache.

### Situação

**Confirmada para controlar o escopo.**

---

## 17. Adiar recursos operacionais avançados

### Decisão

Ficam fora do MVP:

- checkpoints detalhados;
- retomada exata;
- agendamento;
- hospedagem;
- Docker;
- PostgreSQL;
- múltiplas redes;
- classificação ampla, regional e limitada;
- histórico analítico completo da cobertura.

### Motivo

Esses recursos melhoram operação e análise, mas não são necessários para provar o fluxo completo.

### Situação

**Confirmada.**

---

# Parte V — Filmes em cartaz

## 18. Não publicar todos os filmes encontrados

### Problema

A coleta nacional encontrou títulos presentes em quase toda a rede e títulos presentes em pouquíssimos cinemas.

### Decisão

Coletar todos, mas publicar somente os que atingirem relevância nacional.

### Situação

**Confirmada.**

---

## 19. Calcular cobertura por cinema e estado

### Fórmulas

```python
theater_coverage = movie_theater_count / processed_theater_count
state_coverage = movie_state_count / processed_state_count
```

### Motivo

A cobertura por estado reduz a distorção provocada por regiões com muitos cinemas.

### Situação

**Confirmada.**

---

## 20. Adotar limite nacional inicial de 80%

### Decisão

Um filme em cartaz será elegível quando:

```text
cobertura em cinemas >= 80%
e
cobertura em estados >= 80%
```

### Motivo

A prova de conceito revelou um corte forte entre os títulos quase universais e o grupo seguinte.

### Por que não 100%

Exigir 100% seria sensível a falhas pontuais, programação atrasada e diferenças temporárias.

### Situação

**Confirmada e configurável.**

---

## 21. Reavaliar filmes abaixo do limite

### Decisão

Um filme abaixo do limite não será descartado.

### Motivo

A distribuição pode crescer ao longo dos dias.

### Comportamento

- salvar o filme;
- salvar a observação;
- não criar publicação;
- recalcular nas próximas execuções;
- publicar quando cruzar o limite.

### Situação

**Confirmada.**

---

# Parte VI — Filmes em breve organizados por data

## 22. Substituir o filtro geográfico de `em_breve` por uma janela de data

### Decisão

A publicação `em_breve` será determinada pela proximidade da estreia.

```text
0 <= dias_ate_estreia <= 7
```

### Motivo

Para um lançamento futuro, o dado mais útil para o público é saber que a estreia acontecerá na próxima semana.

A distribuição futura pode ser cadastrada gradualmente e não precisa obedecer ao mesmo filtro usado para filmes já em cartaz.

### Situação

**Confirmada.**

---

## 23. Enviar na primeira execução realizada dentro da janela

### Decisão

Como o MVP será manual, a mensagem não depende de uma execução exatamente sete dias antes.

Exemplos:

```text
Faltam 7 dias → enviar
Faltam 4 dias → enviar
Falta 1 dia → enviar
Estreia hoje → enviar
Data já passou → não enviar como em_breve
```

### Situação

**Confirmada.**

---

## 24. Exigir data válida para `em_breve`

### Decisão

Um filme sem `release_date` válida será salvo, mas não será publicado na categoria `em_breve`.

### Motivo

Sem data, a aplicação não consegue provar que a estreia está dentro da janela de sete dias.

### Situação

**Confirmada.**

---

## 25. Consultar detalhes antes da elegibilidade de `em_breve`

### Problema

A listagem `commingSoon` observada não fornece necessariamente a data de estreia.

### Decisão

Para filmes em breve, `detailBySlug` deverá ser consultado antes da avaliação da janela quando a data ainda não estiver disponível ou precisar ser atualizada.

### Diferença entre as categorias

```text
EM CARTAZ
cobertura → filtro → detalhes

EM BREVE
detalhes/data → janela de 7 dias
```

### Consequência

A coleta de `em_breve` poderá realizar mais consultas de detalhes que a coleta de `em_cartaz`.

### Situação

**Confirmada.**

---

## 26. Não republicar automaticamente quando a data mudar

### Decisão

Depois que houver uma publicação `em_breve`, uma mudança na data atualizará o banco, mas não criará outra mensagem no MVP.

### Motivo

Avisos de adiamento ou antecipação exigem uma regra própria e poderiam gerar duplicidades ou ruído.

### Evolução

Criar um tipo de evento específico para mudança de estreia.

### Situação

**Confirmada para o MVP.**

---

# Parte VII — Primeira execução

## 27. Publicar todos os candidatos elegíveis

### Decisão

A primeira execução não será usada apenas para criar uma linha de base.

### `em_cartaz`

Todos os filmes que passarem pelo filtro de 80% em cinemas e estados serão publicados.

### `em_breve`

Todos os filmes que estiverem entre zero e sete dias da estreia serão publicados.

### Motivo

Isso permite demonstrar imediatamente o projeto e popular o canal com o conteúdo que atende às regras atuais.

### Situação

**Confirmada.**

---

# Parte VIII — Persistência

## 28. Separar filme conhecido de publicação confirmada

### Decisão

O banco terá três responsabilidades:

```text
movies
→ identidade e detalhes

movie_observations
→ estado observado e elegibilidade

publications
→ mensagens confirmadas pelo Telegram
```

### Motivo

Um filme pode ser conhecido sem ser elegível e pode ser elegível sem ter sido entregue com sucesso.

### Situação

**Confirmada.**

---

## 29. Salvar filmes antes do Telegram

### Decisão

`movies` e `movie_observations` serão salvos antes da tentativa de envio.

### Consequências positivas

Isso permite:

- acompanhar filmes abaixo do limite;
- guardar lançamentos antes da janela de sete dias;
- recalcular elegibilidade;
- atualizar datas e detalhes;
- repetir a tentativa quando o Telegram falhar;
- distinguir descoberta de entrega.

### Isso aumenta muito o projeto?

Não.

A estrutura com três tabelas já era prevista. A principal mudança é tornar a ordem explícita e usar `publications` como fonte de verdade.

### Situação

**Confirmada.**

---

## 30. Registrar publicação somente depois do Telegram

### Decisão

```text
salvar filme e observação
        ↓
enviar ao Telegram
        ↓
confirmou?
    não → publications permanece vazia
    sim → inserir publication
```

### Motivo

Se a publicação fosse gravada antes do envio, uma falha do Telegram faria a aplicação acreditar que a mensagem já foi entregue.

### Risco aceito

O Telegram pode aceitar a mensagem e o processo falhar antes de gravar `publications`. Isso poderá gerar duplicidade na próxima execução.

Eliminar completamente essa janela exigiria fila persistente, outbox ou estados transacionais adicionais, considerados exagero para o MVP.

### Situação

**Confirmada.**

---

# Parte IX — Telegram

## 31. Enviar pôster com legenda

### Decisão

A forma principal será `sendPhoto` com URL HTTPS do pôster.

### Ordem de preferência

```text
1. desktop_poster_image
2. mobile_poster_image
3. tablet_poster_image
```

### Situação

**Incluída no MVP.**

---

## 32. Usar fallback em texto

### Decisão

Se não houver pôster válido ou `sendPhoto` falhar, tentar `sendMessage`.

### Regra

```text
foto funcionou → photo
texto funcionou → text_fallback
ambos falharam → sem publication
```

### Situação

**Incluída no MVP.**

---

## 33. Limitar a legenda a 1000 caracteres

### Decisão

```python
TELEGRAM_CAPTION_LIMIT = 1000
```

### Motivo

Deixar margem abaixo do limite máximo da legenda e evitar erros por conteúdo variável.

### Regra

Somente a sinopse poderá ser reduzida. Links e dados obrigatórios serão preservados.

### Situação

**Confirmada.**

---

# Parte X — Cabeçalhos HTTP

## 34. Resultado histórico dos testes

### Observação da prova de conceito

Os endpoints de filmes aceitaram requisições relativamente simples.

Os endpoints de localização retornaram `403` em alguns testes com um `User-Agent` simplificado e funcionaram quando foram reproduzidos cabeçalhos públicos do navegador.

### Problema da primeira solução

Copiar permanentemente cabeçalhos como:

```text
sec-ch-ua
sec-ch-ua-mobile
sec-ch-ua-platform
Chrome/150
```

pode deixar o cliente preso a uma versão específica e incluir dados que não são realmente necessários.

### Situação

O conjunto completo funcionou na prova de conceito, mas ainda não foi reduzido ao mínimo necessário.

---

## 35. Verificação atual dos endpoints de filmes

Em **14 de julho de 2026**, foram verificadas novamente respostas JSON válidas nos endpoints:

```text
/movies/onDisplayByTheater
/movies/commingSoon
/movies/detailBySlug
```

As respostas continham `success: true` e a estrutura esperada de listagem ou detalhes.

Essa verificação confirma que os endpoints principais do MVP continuavam ativos nessa data.

Ela não substitui o teste local de cabeçalhos porque o ambiente de verificação não permite controlar exatamente cada cabeçalho enviado.

---

## 36. Retirar o problema de cabeçalhos do caminho crítico do MVP

### Decisão

Como o MVP utilizará um cache pronto de localizações, ele não dependerá inicialmente dos endpoints `/states`, `/cities` e `/theaters`.

### Motivo

Esses eram os endpoints que apresentaram maior sensibilidade aos cabeçalhos.

### Consequência

O perfil definitivo para esses endpoints poderá ser validado antes da primeira atualização, sem impedir a entrega do monitor principal.

### Situação

**Confirmada.**

---

## 37. Experimento obrigatório para reduzir cabeçalhos

Antes de implementar `refresh_locations.py`, deverá ser criado e executado um teste controlado.

### Objetivo

Encontrar o menor conjunto de cabeçalhos que permita consultar todos os endpoints necessários sem copiar dados desnecessários de uma versão específica do navegador.

### Endpoints do teste

```text
/states?hasCinemark=true
/cities?hasCinemark=true&stateId=<id_valido>
/theaters?cityId=<id_valido>
/movies/onDisplayByTheater?theaterId=<id_valido>
/movies/commingSoon?cityId=<id_valido>
/movies/detailBySlug?slug=<slug_valido>
```

### Perfis que deverão ser testados

```text
P0 — requests padrão, sem cabeçalhos adicionais

P1 — Accept: application/json

P2 — P1 + User-Agent comum

P3 — P2 + Origin + Referer

P4 — P3 + Accept-Language

P5 — conjunto completo copiado do navegador
```

### Ordem de execução

1. testar P0 em todos os endpoints;
2. registrar status, `Content-Type` e marcador `success`;
3. quando um perfil falhar, testar o perfil seguinte;
4. usar intervalo de pelo menos 1,5 segundo;
5. interromper imediatamente se aparecer bloqueio da Cloudflare;
6. não continuar gerando requisições inválidas;
7. repetir o teste em outro momento somente se a fonte não estiver bloqueada.

### Resultado esperado

Criar uma matriz como:

```text
Endpoint                     P0   P1   P2   P3   P4   P5
states                       403  403  403  200  200  200
cities                       403  403  403  200  200  200
theaters                     403  403  403  200  200  200
onDisplayByTheater           200  200  200  200  200  200
commingSoon                  200  200  200  200  200  200
detailBySlug                 200  200  200  200  200  200
```

Os valores acima são apenas o formato esperado da matriz, não resultados já comprovados.

### Critério de escolha

Selecionar o menor perfil que passe em todos os endpoints necessários.

Se os endpoints de localização precisarem de um perfil maior, poderá ser utilizado:

- um perfil mínimo para filmes;
- outro perfil mínimo para localizações.

Não existe obrigação de usar o mesmo conjunto para todos.

### Dados a registrar

Para cada tentativa:

- data e hora;
- endpoint;
- perfil;
- status HTTP;
- `Content-Type`;
- tamanho da resposta;
- JSON válido ou não;
- valor de `success`;
- presença de `Cloudflare` ou `Attention Required`;
- duração da requisição.

### Situação

**Experimento definido; execução local pendente antes da atualização automática de localizações.**

---

## 38. Conjunto inicial dos endpoints do MVP

Para os endpoints de filmes, a implementação começará com um conjunto centralizado e pequeno:

```python
HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Origin": "https://www.cinemark.com.br",
    "Referer": "https://www.cinemark.com.br/",
    "User-Agent": "<valor centralizado e configurável>",
}
```

Cabeçalhos `sec-ch-*` só serão adicionados quando um teste demonstrar necessidade.

### Situação

**Regra definida.**

---

# Parte XI — Qualidade e implementação

## 39. Usar Python e SQLite

### Decisão

Stack principal:

```text
Python 3.12+
requests
sqlite3
python-dotenv
pytest
ruff
Telegram Bot API
```

### Motivo

Essa stack é suficiente para o fluxo atual e evita framework web ou infraestrutura sem necessidade.

### Situação

**Confirmada.**

---

## 40. Não usar framework web no MVP

### Decisão

FastAPI, Flask e Django ficam fora da primeira entrega.

### Motivo

O programa será iniciado pelo terminal e não possui frontend ou consumidor de uma API própria.

### Situação

**Confirmada.**

---

## 41. Separar responsabilidades

### Decisão

Usar módulos separados para:

- cliente da Cinemark;
- cache de localizações;
- agregação nacional;
- elegibilidade;
- banco;
- Telegram;
- formatação;
- seleção de pôster;
- modelos e exceções.

### Motivo

Evitar um único arquivo grande sem introduzir microserviços ou abstrações genéricas.

### Situação

**Confirmada.**

---

## 42. Preservar experimentos

### Decisão

Os scripts que documentam a investigação ficarão em `experiments/`.

### Motivo

Eles demonstram:

- tentativa de scraping;
- descoberta da BFF;
- validação de endpoints;
- mapeamento nacional;
- deduplicação;
- bug de normalização;
- análise de cobertura;
- futura redução de cabeçalhos.

### Situação

**Confirmada.**

---

## 43. Testar regras puras sem internet

### Decisão

`pytest` deverá cobrir principalmente:

- normalização;
- deduplicação;
- paginação;
- cobertura;
- limite nacional;
- janela de sete dias;
- persistência;
- seleção de pôster;
- formatação;
- campos ausentes.

### Motivo

A maior parte da lógica crítica pode ser testada com fixtures, sem depender da disponibilidade da Cinemark ou do Telegram.

### Situação

**Confirmada.**

---

## 43.1 Seguir as convenções da PEP 8

### Decisão

O código oficial do projeto seguirá as convenções da PEP 8 para nomes, imports, indentação, espaços e organização geral.

### Motivo

Adotar uma convenção reconhecida torna o código mais previsível para outras pessoas, reduz decisões visuais repetidas e demonstra familiaridade com o padrão mais comum do ecossistema Python.

A PEP 8 orientará a escrita, mas não substituirá decisões de arquitetura, bons nomes ou separação correta de responsabilidades.

### Situação

**Confirmada.**

---

## 43.2 Usar Ruff como formatador e analisador estático

### Decisão

O Ruff fará parte das dependências de desenvolvimento e será usado com:

```bash
ruff format .
ruff check .
ruff check --fix .
```

A configuração inicial habilitará regras de erros importantes, Pyflakes, organização de imports e convenções de nomes:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I", "N"]
```

### Motivo

O Ruff reúne formatação e análise estática em uma ferramenta rápida. Além de apontar problemas, ele pode corrigir automaticamente formatação, imports e outras ocorrências consideradas seguras.

### Limites

O Ruff não prova que as regras de negócio funcionam, não substitui o `pytest` e não decide sozinho se uma arquitetura ou um nome comunica bem a intenção.

### Situação

**Confirmada.**

---

## 43.3 Adotar o `src layout`

### Alternativas consideradas

- manter todos os módulos Python na raiz;
- utilizar `src/movies_on_my_radar/`;
- criar desde o início várias subpastas de camadas dentro do pacote.

### Decisão

O código oficial ficará em:

```text
src/
└── movies_on_my_radar/
```

Testes, dados, experimentos, documentos e configurações permanecerão fora do pacote.

### Motivo

O `src layout` isola o código importável, reduz o risco de os testes importarem arquivos diretamente da raiz por acidente e aproxima o ambiente de desenvolvimento da forma como o pacote será realmente instalado.

A pasta `src/` representa a área de código-fonte. A pasta `movies_on_my_radar/` representa o pacote Python. Essa estrutura em cascata não significa duplicação do projeto.

### Controle de complexidade

O pacote começará com módulos simples. Pastas como `clients/`, `services/` e `repositories/` somente serão adicionadas quando houver código suficiente para justificá-las.

### Consequência

O ambiente deverá instalar o projeto em modo editável:

```bash
python -m pip install -e ".[dev]"
```

A aplicação poderá ser executada com:

```bash
python -m movies_on_my_radar
```

### Situação

**Confirmada.**

---

## 43.4 Centralizar o projeto no `pyproject.toml`

### Decisão

O `pyproject.toml` será a fonte principal para:

- metadados;
- dependências da aplicação;
- dependências de desenvolvimento;
- sistema de build;
- descoberta do pacote em `src/`;
- configuração do pytest;
- configuração do Ruff.

O MVP não manterá também uma lista manual paralela em `requirements.txt`.

### Motivo

Um único arquivo reduz duplicação e permite preparar o ambiente de desenvolvimento com:

```bash
python -m pip install -e ".[dev]"
```

O `pip` lerá o projeto e instalará as dependências declaradas sem que cada pacote precise ser instalado por um comando separado.

### Limites

O arquivo não descobre novas dependências automaticamente a partir dos imports. Quando uma biblioteca for adicionada ao código, ela também deverá ser declarada no `pyproject.toml`.

Segredos e configurações de execução continuarão no `.env`. Documentação continuará nos arquivos Markdown.

Um arquivo de lock ou de versões exatas poderá ser introduzido futuramente se a implantação exigir reprodução idêntica do ambiente.

### Situação

**Confirmada.**

---

# Parte XII — Estado atual

## 44. O que já está validado

```text
Acesso à página e investigação do HTML
✅

Descoberta da BFF
✅

Listagem em cartaz por cinema
✅

Listagem em breve por cidade
✅

Detalhes por slug
✅

Descoberta nacional de localizações
✅ prova de conceito

Deduplicação nacional de cinemas
✅ prova de conceito

Deduplicação nacional de filmes em cartaz
✅ prova de conceito

Cobertura por cinema
✅

Cobertura por estado
✅ viável com os dados coletados

Limite nacional inicial de 80%
✅ decidido

Janela de sete dias para em_breve
✅ decidida

Ordem de persistência
✅ decidida
```

---

## 45. O que ainda precisa ser implementado

- estrutura oficial do repositório;
- leitura e validação do cache;
- cliente modular da Cinemark;
- coleta nacional em cartaz;
- coleta nacional em breve;
- regra de datas;
- banco SQLite;
- Telegram;
- pôster e fallback;
- testes automatizados;
- resumo da execução;
- documentação pública.

---

## 46. O que fica para depois do MVP

### Primeira atualização

- `refresh_locations.py`;
- experimento local de cabeçalhos mínimos;
- atualização automática do cache;
- checkpoints;
- retomada;
- classificações ampla, regional e limitada;
- avisos de mudança de estreia.

### Evoluções futuras

- automação e hospedagem;
- Docker e PostgreSQL;
- WhatsApp;
- IA;
- outras redes de cinema;
- painel;
- usuários e preferências.

---

## 47. Evolução resumida do conceito

```text
IDEIA 1
HTML + BeautifulSoup
        ↓
DESCOBERTA
O HTML não continha os cards úteis
        ↓
IDEIA 2
Consumir BFF JSON
        ↓
PROVA LOCAL
Um theaterId e um cityId
        ↓
PROVA NACIONAL
Estados → cidades → cinemas
        ↓
AGREGAÇÃO
616 ocorrências → 22 filmes únicos
        ↓
RELEVÂNCIA
80% de cinemas e estados
        ↓
REGRA DE DATA
em_breve dentro de 7 dias
        ↓
MVP CONTROLADO
cache pronto + filmes + SQLite + Telegram
```

---

## 48. Conclusão

O Movies on my radar cresceu em relação à ideia inicial, mas o crescimento veio de descobertas reais, não de funcionalidades inventadas.

A solução para manter o projeto executável é preservar o diferencial nacional e retirar do MVP as partes operacionais que não são necessárias para provar o produto.

O MVP atual continua significativo para portfólio porque demonstra:

- investigação de uma aplicação web;
- consumo de API interna não documentada;
- agregação de dados nacionais;
- deduplicação;
- regras temporais e geográficas;
- persistência correta;
- integração com Telegram;
- testes e documentação.

A definição técnica final do projeto será:

> Backend em Python que consome a BFF utilizada pelo site da Cinemark, agrega filmes nacionalmente, envia próximos lançamentos dentro de uma janela de sete dias, publica filmes em cartaz com cobertura nacional e registra separadamente observações e entregas confirmadas.
