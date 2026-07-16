# Referência 2 — Catálogo de Anti-Patterns (Fase 2)

Cada anti-pattern traz **sinais de detecção acionáveis** e uma **severidade
padrão**. A severidade pode subir/descer conforme o impacto real no projeto (ver
escala no fim). Percorra todos os arquivos e registre cada ocorrência com
`arquivo:linha`.

> Referência de severidade: **CRITICAL** = falha de segurança ou arquitetura que
> quebra o funcionamento/expõe dados; **HIGH** = forte violação de MVC/SOLID que
> trava manutenção e testes; **MEDIUM** = padronização, duplicação, performance
> moderada; **LOW** = legibilidade, nomes, magic numbers.

---

## AP-01 · Hardcoded Credentials / Secrets — `CRITICAL`
Segredos embutidos no código-fonte.
**Sinais:** literais como `SECRET_KEY = "..."`, `password = "..."`,
`paymentGatewayKey`, `dbPass`, `api_key`, tokens `pk_live_...`, senhas SMTP;
segredos versionados em vez de variáveis de ambiente.
**Impacto:** vazamento de credenciais; comprometimento total ao publicar o repo.
**Corrigir:** mover para config/env (`os.environ`, `process.env`, `.env`).

## AP-02 · SQL Injection / Query por Concatenação — `CRITICAL`
Entrada do usuário concatenada dentro de SQL.
**Sinais:** `"... WHERE id = " + str(id)`, f-strings/template literals em SQL
(`f"... {email}"`, `` `... ${x}` ``), `"LIKE '%" + termo + "%'"`. Ausência de
placeholders (`?`, `%s`, `:param`).
**Impacto:** leitura/escrita/destruição arbitrária de dados.
**Corrigir:** queries parametrizadas ou ORM.

## AP-03 · Endpoint Perigoso / Superfície de Ataque — `CRITICAL`
Rota que executa comandos arbitrários ou operações destrutivas sem auth.
**Sinais:** `/admin/query` executando SQL vindo do request; `/reset-db` sem
autenticação; `eval`/`exec` sobre entrada do usuário.
**Impacto:** RCE/SQL arbitrário, perda total de dados.
**Corrigir:** remover; se necessário, proteger com auth + operação restrita.

## AP-04 · Senha em Texto Puro / Hash Fraco / Exposição de Senha — `CRITICAL`
Credenciais mal protegidas.
**Sinais:** senha salva/comparada em texto puro; `hashlib.md5`/`sha1` para senha;
hash caseiro (loop de `base64`); campo `password`/`senha` presente na resposta
serializada (`to_dict`) da API.
**Impacto:** vazamento de credenciais dos usuários.
**Corrigir:** bcrypt/argon2/PBKDF2; **nunca** serializar a senha na resposta.

## AP-05 · God Class / God Module — `CRITICAL`
Um único arquivo/classe concentra tudo (DB + rotas + regra de negócio +
validação) para múltiplos domínios.
**Sinais:** arquivo com centenas de linhas cobrindo entidades distintas; classe
`Manager`/`Service` que abre conexão de banco, registra rotas e processa
pagamento; models que também formatam relatório e enviam notificação.
**Impacto:** impossível testar em isolamento; qualquer mudança afeta tudo.
**Corrigir:** separar em Models/Controllers/Services por domínio.

## AP-06 · Fat Controller / Lógica de Negócio na Camada Errada — `HIGH`
Regra de negócio presa em rotas/controllers ou dentro de models de dados.
**Sinais:** cálculo de desconto/relatório dentro do handler de rota; envio de
e-mail/SMS/push no controller; montagem de relatório de 80 linhas na view; regras
de status/pagamento no meio do roteamento.
**Impacto:** baixa testabilidade, duplicação, acoplamento.
**Corrigir:** extrair para Services/Models; controller só orquestra.

## AP-07 · Estado Global Mutável / Acoplamento sem Injeção de Dependência — `HIGH`
Singletons mutáveis e dependências instanciadas "por dentro".
**Sinais:** `global db_connection`; `let globalCache = {}`, `let totalRevenue = 0`
em escopo de módulo; conexão de banco criada dentro de cada função; `new X()`
hardcoded em vez de receber por parâmetro; `check_same_thread=False` num singleton
compartilhado.
**Impacto:** estado imprevisível, condições de corrida, difícil de testar.
**Corrigir:** injeção de dependência; ciclo de vida de recursos explícito.

## AP-08 · Callback Hell / Fluxo Assíncrono Manual — `HIGH`
Pirâmide de callbacks aninhados e controle manual de concorrência.
**Sinais:** callbacks de DB aninhados 3+ níveis; contadores manuais
(`coursesPending--`, `if (x === 0) res.json(...)`) para sincronizar respostas;
`self = this` para contornar escopo.
**Impacto:** race conditions, respostas duplicadas, erros silenciosos.
**Corrigir:** `async/await` + Promises (ou driver com API de promises).

## AP-09 · N+1 Queries / Gargalo de Performance — `MEDIUM`
Consulta ao banco dentro de laço.
**Sinais:** `for item in itens: cursor.execute("SELECT ... WHERE id = ...")`;
`courses.forEach(... db.all(...))`; `len(u.tasks)` disparando lazy-load por
usuário; recalcular agregados em Python quando o SQL faria com `JOIN`/`COUNT`.
**Impacto:** latência que cresce linearmente com os dados.
**Corrigir:** `JOIN`/`IN`/agregação no banco; carregar em lote.

## AP-10 · Validação Ausente/Duplicada & Tratamento de Erro Pobre — `MEDIUM`
Regras de validação espalhadas/repetidas e captura de erro genérica.
**Sinais:** blocos idênticos de validação copiados entre `criar` e `atualizar`;
`except:`/`catch {}` que engolem o erro; ausência de validação em rotas que
gravam; lógica de "overdue" duplicada em vários lugares.
**Impacto:** inconsistência, bugs mascarados, DRY violado.
**Corrigir:** validador/serializer central; middleware de erro; extrair helpers.

## AP-11 · API Deprecated / Obsoleta — `MEDIUM` (sobe se remove segurança)
Uso de APIs marcadas como deprecated pela linguagem/framework.
**Sinais e equivalente moderno:**
| Deprecated | Onde | Substituir por |
|---|---|---|
| `datetime.utcnow()` | Python 3.12+ | `datetime.now(datetime.UTC)` (timezone-aware) |
| `Model.query.get(id)` | SQLAlchemy 2.0 (LegacyAPIWarning) | `db.session.get(Model, id)` |
| `Query.get_or_404` legado / `Model.query` pattern | Flask-SQLAlchemy 3+ | `db.session.execute(db.select(...))` |
| `body-parser` avulso | Express 4.16+ | `express.json()` embutido |
| `crypto.createCipher` | Node | `crypto.createCipheriv` |
| `new Buffer(...)` | Node | `Buffer.from(...)` |
| `datetime.datetime.strptime` sem tz em código novo | — | manter, mas normalizar tz |
**Impacto:** quebra em versões futuras; warnings; comportamento sutil (tz-naive).
**Corrigir:** trocar pelo equivalente moderno indicado.

## AP-12 · Logging via `print`/`console.log` & Observabilidade — `LOW`
Saída de diagnóstico improvisada.
**Sinais:** `print("ERRO: "+...)`, `console.log(...)` para erros/negócio;
**log de dado sensível** (nº de cartão, chave de pagamento) — isso **sobe para
CRITICAL**.
**Corrigir:** logger estruturado com níveis; nunca logar segredo/dado sensível.

## AP-13 · Magic Numbers / Strings & Nomenclatura Ruim — `LOW`
Constantes soltas e nomes não descritivos.
**Sinais:** thresholds `10000`/`5000` de desconto sem nome; status/roles como
strings repetidas; variáveis `u`, `e`, `p`, `cc`, `cid`; `card.startsWith("4")`
como regra de pagamento.
**Corrigir:** constantes nomeadas/enums; nomes descritivos.

## AP-14 · Código Morto / Imports Não Usados — `LOW`
Ruído que engana o leitor.
**Sinais:** `import os, sys, json, time` sem uso; funções nunca chamadas; serviço
declarado mas nunca acionado (ex.: `NotificationService` não integrado).
**Corrigir:** remover imports/código não usados; integrar ou remover o serviço.

---

## Escala de Severidade (para classificar/reclassificar)

- **CRITICAL** — Segurança (credenciais, injection, senha) ou arquitetura que
  impede o funcionamento correto / viola totalmente a separação de camadas.
- **HIGH** — Forte violação de MVC/SOLID: negócio na camada errada, acoplamento
  sem DI, estado global mutável, fluxo assíncrono não gerenciado.
- **MEDIUM** — Padronização, duplicação, performance moderada (N+1), validação
  ausente, API deprecated.
- **LOW** — Legibilidade, nomes, magic numbers, logging improvisado, código morto.

**Requisito mínimo por auditoria:** ≥ 5 findings, sendo ≥ 1 `CRITICAL` ou `HIGH`.
