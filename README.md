# Skill de Auditoria e Refatoração Arquitetural — `refactor-arch`

Este repositório entrega uma **Custom Skill do Claude Code** (`refactor-arch`) que
audita e refatora projetos de backend legados para o padrão **MVC**, de forma
**agnóstica de tecnologia**, em 3 fases: **Análise → Auditoria (com confirmação)
→ Refatoração (com validação)**.

A skill foi aplicada aos 3 projetos fornecidos:

| # | Projeto | Stack | Ponto de partida |
|---|---|---|---|
| 1 | `code-smells-project` | Python + Flask (SQL cru) | Monolito sem camadas |
| 2 | `ecommerce-api-legacy` | Node.js + Express | God Class + callback hell |
| 3 | `task-manager-api` | Python + Flask + SQLAlchemy | Parcialmente em camadas |

> A especificação original do desafio está em [`PLAN.md`](./PLAN.md). Os relatórios
> de auditoria gerados estão em [`reports/`](./reports).

---

## A) Análise Manual

Problemas identificados manualmente na leitura do código (mínimo 5 por projeto, com
≥1 CRITICAL/HIGH, ≥2 MEDIUM, ≥2 LOW). A lista completa com arquivo:linha está nos
relatórios em `reports/`.

### Projeto 1 — code-smells-project (Flask)

| Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|
| CRITICAL | SQL Injection generalizado | `models.py` (queries concatenadas) | Entrada do usuário concatenada no SQL permite dump/DROP e bypass de login. |
| CRITICAL | Segredo hardcoded + DEBUG on | `app.py:7-8` | Chave versionada e stack traces expostos em produção. |
| CRITICAL | Endpoint de SQL arbitrário | `app.py:59-78` (`/admin/query`) | Executa qualquer SQL do request — equivalente a shell no banco. |
| CRITICAL | Senha em texto puro e exposta | `models.py:83,109-129` | Credenciais gravadas/retornadas sem hash. |
| MEDIUM | N+1 na leitura de pedidos | `models.py:187-231` | Uma query por item dentro do laço; latência linear. |
| MEDIUM | Validação duplicada | `controllers.py:28-90` | Regras copiadas entre criar/atualizar (DRY). |
| LOW | Logging via `print` | `controllers.py` (vários) | Observabilidade pobre. |
| LOW | Magic numbers de desconto | `models.py:257-262` | Limiares soltos sem nome. |

### Projeto 2 — ecommerce-api-legacy (Express)

| Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|
| CRITICAL | God Class | `AppManager.js:4-141` | DB + rotas + pagamento + relatório numa classe só. |
| CRITICAL | Credenciais hardcoded | `utils.js:2-5` | Chave do gateway e senha de DB no código. |
| CRITICAL | Log de cartão + chave | `AppManager.js:45` | Vaza PAN e segredo no stdout (PCI/LGPD). |
| CRITICAL | Hash de senha caseiro | `utils.js:17-23` | `badCrypto` reversível e sem sal. |
| HIGH | Callback hell | `AppManager.js:37-128` | Aninhamento e contadores manuais → race conditions. |
| MEDIUM | N+1 no relatório financeiro | `AppManager.js:83-128` | Query por curso/matrícula/usuário/pagamento. |
| MEDIUM | Deleção sem integridade | `AppManager.js:131-137` | Deixa matrículas/pagamentos órfãos. |
| LOW | Nomes crípticos / magic strings | `AppManager.js:29-47` | `u`, `e`, `cc`; regra "cartão começa com 4". |

### Projeto 3 — task-manager-api (Flask + SQLAlchemy)

| Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|
| CRITICAL | Segredos hardcoded | `app.py:13`, `notification_service.py:10` | SECRET_KEY e senha SMTP no código. |
| HIGH | Hash MD5 de senha | `user.py:27-32` | MD5 sem sal é quebrável. |
| HIGH | Hash de senha exposto | `user.py:16-25` (`to_dict`) | Retornado no login/cadastro/detalhe. |
| HIGH | Lógica de negócio nas rotas | `report_routes.py:12-101` | Controllers gordos, service layer não usado. |
| MEDIUM | N+1 no summary | `report_routes.py:53-68` | Query de tasks por usuário no laço. |
| MEDIUM | APIs deprecated | `datetime.utcnow()`, `Query.get()` (vários) | Deprecated no Python 3.12+/SQLAlchemy 2.0. |
| LOW | Overdue duplicado | 4+ lugares | Mesma regra reescrita (DRY). |
| LOW | Imports não usados | rotas + `helpers.py` | Ruído de dependências inexistentes. |

---

## B) Construção da Skill

### Estrutura

```
.claude/skills/refactor-arch/
├── SKILL.md                          # Orquestrador das 3 fases (o "prompt")
└── references/                       # Conhecimento de domínio (o "manual")
    ├── 01-project-analysis.md        # Heurísticas de detecção de stack/DB/arquitetura
    ├── 02-antipattern-catalog.md     # 14 anti-patterns + severidade + APIs deprecated
    ├── 03-report-template.md         # Formatos de saída das 3 fases
    ├── 04-architecture-guidelines.md # Regras do MVC alvo
    └── 05-refactoring-playbook.md    # 12 padrões de transformação antes/depois
```

### Decisões de design

- **`SKILL.md` é o prompt, referências são o conhecimento.** O `SKILL.md`
  orquestra o fluxo e manda "ler o arquivo X antes da fase Y"; o conhecimento
  denso (catálogo, playbook) fica nas referências, carregadas sob demanda.
- **Confirmação obrigatória na Fase 2.** A skill gera o relatório, salva em
  `reports/` e **para**, pedindo `[y/n]` antes de tocar em qualquer arquivo.
- **Validação obrigatória na Fase 3.** Só declara sucesso após boot limpo +
  endpoints respondendo + zero CRITICAL remanescente.

### Anti-patterns incluídos (14) e por quê

Cobrem as 4 severidades e os problemas reais dos 3 projetos: segredos hardcoded,
SQL Injection, endpoint perigoso, senha fraca/exposta (CRITICAL); God Class, fat
controller, estado global sem DI, callback hell (HIGH); N+1, validação/erro pobre,
**APIs deprecated** (MEDIUM); logging por `print`, magic numbers, código morto
(LOW). O catálogo inclui uma seção dedicada a **APIs deprecated** com o equivalente
moderno (ex.: `datetime.utcnow()` → `datetime.now(UTC)`, `Query.get()` →
`db.session.get()`, `new Buffer()` → `Buffer.from()`).

### Como garanti que é agnóstica de tecnologia

- Detecção por **evidência** (manifestos, extensões, imports) em vez de suposição.
- Sinais de detecção **acionáveis** e válidos em várias linguagens
  ("query dentro de laço", "concatenação de entrada no SQL").
- O playbook mostra o mesmo padrão em **Python e Node** lado a lado.
- Provada nos **3 projetos** (2 Flask com organizações diferentes + 1 Express) —
  a mesma pasta `.claude/skills/refactor-arch/` foi copiada sem alteração.

### Desafios encontrados

- **Preservar contratos** dos endpoints ao reestruturar (mesmas rotas/respostas).
  Solução: baseline de rotas + smoke tests antes/depois.
- **Endpoints inseguros por design** (SQL arbitrário, reset sem auth): removidos/
  protegidos e **documentados** no relatório, em vez de mantidos.
- **datetime tz-naive x tz-aware**: `now_utc()` retorna UTC naive para não quebrar
  comparações com as colunas existentes ao remover `datetime.utcnow()`.

---

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| 1 — code-smells-project | 5 | 3 | 2 | 3 | **13** |
| 2 — ecommerce-api-legacy | 4 | 3 | 2 | 2 | **11** |
| 3 — task-manager-api | 1 | 3 | 3 | 3 | **10** |

### Antes / Depois (estrutura)

| Projeto | Antes | Depois |
|---|---|---|
| 1 | 4 arquivos planos (`app`, `controllers`, `models`, `database`) | `src/` com `config/ models/ controllers/ views/ services/ validators/ middlewares/ + app.py` |
| 2 | `AppManager.js` (God Class) + `utils.js` | `src/` com `config/ models/ controllers/ routes/ services/ middlewares/ database.js + app.js` |
| 3 | `models/ routes/ services/ utils/` (rotas gordas) | + `config/ controllers/ middlewares/` e `services/` de fato usados; app factory |

### Checklist de Validação (preenchido para os 3 projetos)

**Fase 1 — Análise:** ✅ linguagem, ✅ framework, ✅ domínio, ✅ nº de arquivos — corretos nos 3.

**Fase 2 — Auditoria:** ✅ template seguido · ✅ arquivo:linha em cada finding ·
✅ ordenado CRITICAL→LOW · ✅ ≥5 findings (13/11/10) · ✅ APIs deprecated (projeto 3) ·
✅ pausa para confirmação.

**Fase 3 — Refatoração** (por projeto):

| Item | P1 | P2 | P3 |
|---|:--:|:--:|:--:|
| Estrutura MVC | ✅ | ✅ | ✅ |
| Config sem hardcoded | ✅ | ✅ | ✅ |
| Models abstraindo dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram fluxo | ✅ | ✅ | ✅ |
| Error handling central | ✅ | ✅ | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem | ✅ | ✅ | ✅ |

### Logs das aplicações rodando após a refatoração (smoke tests)

**Projeto 1 (Flask):**
```
BOOT OK — app criado
200 GET  /health          {"status":"ok","counts":{"produtos":10,...}}
200 POST /login           {"dados":{...},"sucesso":true,"mensagem":"Login OK"}
401 POST /login (errada)  {"erro":"Email ou senha inválidos"}
201 POST /pedidos         {"dados":{"pedido_id":1,"total":479.7},...}
401 POST /admin/reset-db  {"erro":"Não autorizado"}   # antes: aberto
```

**Projeto 2 (Express):**
```
DRIVER: sqlite3 | BOOT OK
200 POST   /api/checkout                 {"msg":"Sucesso","enrollment_id":2}
400 POST   /api/checkout (cartão 5...)   "Pagamento recusado"
200 GET    /api/admin/financial-report   [{"course":"Clean Architecture","revenue":997,...}]
200 DELETE /api/users/1                  {"msg":"Usuário e dados relacionados removidos"}
# após delete: curso do usuário zera (cascata) — sem órfãos
```

**Projeto 3 (Flask + SQLAlchemy):**
```
ROTAS: 23
200 GET  /tasks/stats     {"total":11,"overdue":2,"completion_rate":10.0,...}
200 POST /login           {"token":"fake-jwt-token-1","user":{...}}   # sem 'password'
200 GET  /reports/summary {"user_productivity":[...]}                 # 1 query agregada
password em /login? False | /users/1? False | POST /users? False
```

### Como a skill se comportou em stacks diferentes

O monolito (P1) exigiu criação de todas as camadas do zero; a God Class Node (P2)
exigiu, além das camadas, a modernização de callbacks para `async/await`; o projeto
já em camadas (P3) exigiu **refinamento** (controllers/serviços, segurança, APIs
deprecated) sem reescrever o que já estava adequado — exatamente a adaptação ao
contexto que a skill prescreve.

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado.
- **Python 3.11+** (projetos 1 e 3) e **Node.js 18+** (projeto 2).

### Rodar a skill em cada projeto

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill executa a Fase 1 (análise), a Fase 2 (auditoria — **pausa pedindo `y`**) e,
após confirmação, a Fase 3 (refatoração + validação).

### Rodar as aplicações refatoradas

```bash
# Projeto 1 — Flask
cd code-smells-project && pip install -r requirements.txt
python src/app.py                     # http://localhost:5000

# Projeto 2 — Express
cd ecommerce-api-legacy && npm install
npm start                             # http://localhost:3000
# (use ecommerce-api-legacy/api.http para exercitar os endpoints)

# Projeto 3 — Flask + SQLAlchemy
cd task-manager-api && pip install -r requirements.txt
python seed.py                        # popula o banco (opcional)
python app.py                         # http://localhost:5000
```

Copie `.env.example` para `.env` em cada projeto e ajuste os segredos.

### Como validar que a refatoração funcionou

1. A aplicação **sobe sem erros**.
2. Os **endpoints originais respondem** (use `api.http`/`curl` ou os smoke tests
   acima).
3. Confira o relatório em `reports/audit-project-N.md`.

> **Nota de ambiente:** neste ambiente de desenvolvimento, o build nativo do
> pacote `sqlite3` (projeto 2) não estava disponível; o `database.js` cai
> automaticamente para o módulo embutido `node:sqlite` (Node ≥ 22), mantendo a
> mesma interface. Em uma máquina com toolchain nativo, o `npm install` usa o
> `sqlite3` normalmente.
