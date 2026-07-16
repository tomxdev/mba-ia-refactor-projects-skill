# Referência 4 — Guidelines de Arquitetura MVC (Fase 3)

O alvo é **MVC em camadas**, agnóstico de linguagem. Cada camada tem uma única
responsabilidade e depende apenas das camadas abaixo dela.

```
Request → View/Route → Controller → Service (opcional) → Model → Banco
                                   ← Middlewares (erro/auth) ←
```

## Responsabilidades por camada

### Config (`config/`)
- Centraliza configuração e **segredos vindos do ambiente** (nunca hardcoded).
- Ex.: `settings.py` lendo `os.environ`; `config.js` lendo `process.env`.
- `DEBUG`/`ENV` derivam do ambiente; padrões seguros para produção.

### Models (`models/`)
- Representam **entidades e acesso a dados** (um arquivo por entidade/agregado).
- Contêm queries **parametrizadas** ou mapeamento ORM.
- Podem conter regras **intrínsecas à entidade** (ex.: `is_overdue`,
  `set_password` com hash forte), mas **não** orquestram HTTP nem formatam
  relatórios de múltiplas entidades.
- **Nunca** serializam campos sensíveis (senha/hash) para fora.

### Views / Routes (`views/` ou `routes/`)
- Apenas **roteamento**: mapeiam método+caminho → função do controller.
- Sem SQL, sem regra de negócio. Em frameworks web, é onde ficam os blueprints/
  routers. Em apps com template, "View" é a renderização.

### Controllers (`controllers/`)
- **Orquestram o fluxo** de uma requisição: extraem/validam entrada, chamam
  Models/Services, montam a resposta HTTP (status + corpo).
- Não contêm SQL nem regra de negócio pesada — delegam.

### Services (`services/`) — opcional, quando há regra de negócio relevante
- Regras que cruzam entidades ou efeitos colaterais: checkout, cálculo de
  relatório, notificações, hashing de pagamento.
- Mantêm controllers finos e testáveis.

### Middlewares (`middlewares/`)
- **Tratamento de erro centralizado** (um handler que traduz exceções → resposta
  padronizada), autenticação, CORS, logging.

### Entry point / Composition Root
- Um único arquivo (`app.py` / `app.js` / `main.*`) que **monta** a aplicação:
  cria o app, carrega config, registra rotas e middlewares, injeta dependências.
- Sem regra de negócio aqui.

## Regras de dependência (SOLID na prática)
- Camadas de cima dependem das de baixo, **nunca o contrário**.
- Dependências (conexão de banco, serviços) são **injetadas**, não criadas
  ad-hoc dentro de funções nem via singleton global mutável.
- Uma responsabilidade por módulo (SRP). Aberto para extensão, fechado para
  modificação (OCP) onde fizer sentido.

## Estruturas-alvo de referência

**Python / Flask (SQL cru → camadas):**
```
src/
├── config/settings.py
├── models/           # produto_model.py, usuario_model.py, pedido_model.py
├── views/routes.py   # (ou routes/ por domínio) — blueprints
├── controllers/      # produto_controller.py, pedido_controller.py, ...
├── services/         # (se houver regra de negócio: relatório, pedidos)
├── middlewares/error_handler.py
├── database.py       # fábrica de conexão + init de schema
└── app.py            # composition root
```

**Node.js / Express (God Class → camadas):**
```
src/
├── config/index.js
├── models/           # userModel.js, courseModel.js, paymentModel.js (queries)
├── routes/           # checkoutRoutes.js, adminRoutes.js, userRoutes.js
├── controllers/      # checkoutController.js, reportController.js, ...
├── services/         # paymentService.js, cryptoService.js
├── middlewares/errorHandler.js
├── database.js       # conexão + schema
└── app.js            # composition root (cria app, injeta deps, sobe server)
```

**Python/Flask já em camadas (refinamento):** manter `models/` e `routes/`, mas
(a) extrair regra de negócio das rotas para `services/`, (b) mover config/segredos
para `config/`, (c) centralizar erro em `middlewares/`, (d) eliminar duplicação
(ex.: cálculo de "overdue") num único helper/serviço.

## Preservação de comportamento (obrigatório)
- **Mesmos** caminhos de rota, métodos HTTP e formato de resposta.
- Se um endpoint precisa ser removido/protegido por segurança (ex.: SQL
  arbitrário, reset sem auth), **documente** a mudança no relatório da Fase 3.
- A validação da Fase 3 confirma boot limpo + endpoints respondendo.
