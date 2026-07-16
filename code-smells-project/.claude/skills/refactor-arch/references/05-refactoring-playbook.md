# Referência 5 — Playbook de Refatoração (Fase 3)

Transformações concretas **antes → depois** para os anti-patterns do catálogo.
Adapte a sintaxe à linguagem detectada; o padrão é o mesmo.

---

## RP-01 · Extrair segredos para config/env (AP-01)

**Antes (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```
**Depois (`config/settings.py`):**
```python
import os
class Settings:
    SECRET_KEY = os.environ["SECRET_KEY"]            # exigido em runtime
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
```
```python
# app.py
app.config.from_object(Settings)
```
**Node (`config/index.js`):**
```js
module.exports = {
  port: process.env.PORT || 3000,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  db: { user: process.env.DB_USER, pass: process.env.DB_PASS },
};
```
Adicione um `.env.example` e garanta que segredos reais não sejam versionados.

---

## RP-02 · SQL parametrizado (AP-02)

**Antes:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**Depois:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
# valide a senha com hash em código, não no SQL
```
Para busca dinâmica, monte a cláusula com placeholders e uma lista de params:
```python
sql = "SELECT * FROM produtos WHERE 1=1"
params = []
if termo:
    sql += " AND (nome LIKE ? OR descricao LIKE ?)"; params += [f"%{termo}%", f"%{termo}%"]
if categoria:
    sql += " AND categoria = ?"; params.append(categoria)
cursor.execute(sql, params)
```

---

## RP-03 · Remover/proteger endpoint perigoso (AP-03)

**Antes:** `/admin/query` executa SQL arbitrário do request; `/admin/reset-db`
sem auth.
**Depois:** **remova** o endpoint de SQL arbitrário. Se uma operação
administrativa for necessária, exponha uma ação específica e protegida:
```python
@admin_bp.post("/admin/reset-db")
@require_admin            # middleware de auth
def reset_db():
    OrderModel.delete_all(); ProductModel.delete_all()
    return {"sucesso": True}
```
Documente a remoção no relatório da Fase 3.

---

## RP-04 · Hashing forte de senha + não expor hash (AP-04)

**Antes:**
```python
# grava/compara em texto puro
"INSERT INTO usuarios (...senha...) VALUES ('" + senha + "')"
self.password = hashlib.md5(pwd.encode()).hexdigest()   # fraco
'password': self.password                               # vaza na resposta
```
**Depois:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pwd): self.password = generate_password_hash(pwd)
def check_password(self, pwd): return check_password_hash(self.password, pwd)

def to_dict(self):   # NUNCA inclui 'password'
    return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}
```
(Node: `bcrypt.hash` / `bcrypt.compare`.)

---

## RP-05 · Quebrar God Class/Module em camadas (AP-05)

**Antes:** `models.py` (350 linhas: SQL + regra + validação de 4 domínios) ou
`AppManager` (DB + rotas + pagamento).
**Depois:** um Model por entidade + Controller por domínio + Service para regra:
```python
# models/produto_model.py
class ProdutoModel:
    def __init__(self, db): self.db = db
    def get_by_id(self, id):
        cur = self.db.cursor(); cur.execute("SELECT * FROM produtos WHERE id = ?", (id,))
        return cur.fetchone()
```
```python
# controllers/produto_controller.py
def buscar_produto(id):
    produto = produto_model.get_by_id(id)
    return (jsonify(produto), 200) if produto else (jsonify({"erro": "não encontrado"}), 404)
```
Rotas passam a apenas mapear caminho → controller.

---

## RP-06 · Mover regra de negócio para Service/Model (AP-06)

**Antes (regra de desconto e notificação dentro do controller/model de dados):**
```python
def relatorio_vendas():
    ...
    if faturamento > 10000: desconto = faturamento * 0.1
    print("ENVIANDO EMAIL: ...")   # efeito colateral no controller
```
**Depois:**
```python
# services/report_service.py
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
def compute_discount(revenue):
    for threshold, rate in DISCOUNT_TIERS:
        if revenue > threshold: return round(revenue * rate, 2)
    return 0.0
```
```python
# controllers/pedido_controller.py — apenas orquestra
def relatorio_vendas():
    return jsonify(report_service.build_sales_report()), 200
```
Notificações vão para um `NotificationService` chamado pelo controller/service.

---

## RP-07 · Injeção de dependência em vez de estado global (AP-07)

**Antes:**
```python
db_connection = None            # singleton global mutável
def get_db():
    global db_connection
    ...
```
**Depois — fábrica + injeção no composition root:**
```python
# database.py
def create_connection(db_path):
    conn = sqlite3.connect(db_path); conn.row_factory = sqlite3.Row
    return conn
```
```python
# app.py (composition root)
db = create_connection(Settings.DB_PATH)
produto_model = ProdutoModel(db)          # injeta a conexão
produto_controller = ProdutoController(produto_model)
```
(Node: instanciar `new UserModel(db)` no `app.js` e passar aos controllers; nada
de `globalCache`/`totalRevenue` no escopo de módulo.)

---

## RP-08 · Callback hell → async/await (AP-08)

**Antes (Node):**
```js
db.get(sql1, [a], (err, r1) => {
  db.get(sql2, [b], (err, r2) => {
    db.run(sql3, [c], function (err) { res.json({ id: this.lastID }); });
  });
});
```
**Depois — promisify + async/await, com transação:**
```js
const { promisify } = require('util');
// no model: this.get = promisify(db.get.bind(db)); this.run = ...
async function checkout(req, res, next) {
  try {
    const course = await courseModel.findActive(req.body.c_id);
    if (!course) return res.status(404).send("Curso não encontrado");
    const userId = await userModel.ensure(req.body);
    const enrollmentId = await enrollmentModel.create(userId, course.id);
    await paymentService.charge(enrollmentId, course.price, req.body.card);
    res.status(200).json({ enrollment_id: enrollmentId });
  } catch (e) { next(e); }   // erro vai ao middleware central
}
```

---

## RP-09 · Eliminar N+1 (AP-09)

**Antes:**
```python
for item in itens:
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
```
**Depois — uma query com `IN` / `JOIN`:**
```python
ids = [it["produto_id"] for it in itens]
placeholders = ",".join("?" * len(ids))
cursor.execute(f"SELECT * FROM produtos WHERE id IN ({placeholders})", ids)
produtos = {row["id"]: row for row in cursor.fetchall()}   # lookup O(1)
```
Com ORM, use `join`/`selectinload` ou agregue no banco (`COUNT`, `SUM`) em vez de
laços Python. Ex.: `task_count` via `func.count` num único `GROUP BY`.

---

## RP-10 · Validação central + middleware de erro (AP-10)

**Antes:** validações duplicadas entre `criar`/`atualizar`; `except:` que engole
erro; lógica de "overdue" repetida em 4 lugares.
**Depois:**
```python
# validators/produto_validator.py
def validate_produto(data):
    errors = []
    if not data.get("nome") or len(data["nome"]) < 2: errors.append("nome inválido")
    if data.get("preco", 0) < 0: errors.append("preço negativo")
    return errors
```
```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle(e):
        app.logger.exception(e)
        return jsonify({"erro": "erro interno"}), 500
```
```python
# models/task_model.py — única fonte de verdade para "overdue"
def is_overdue(self):
    return bool(self.due_date and self.due_date < now_utc()
                and self.status not in ("done", "cancelled"))
```

---

## RP-11 · Substituir APIs deprecated (AP-11)

**Antes → Depois:**
```python
datetime.utcnow()                 # → datetime.now(datetime.UTC)
User.query.get(user_id)           # → db.session.get(User, user_id)
Task.query.filter_by(...).all()   # ok, mas prefira db.session.execute(db.select(Task)...)
```
```js
new Buffer(x)                     // → Buffer.from(x)
crypto.createCipher(...)          // → crypto.createCipheriv(...)
```
Concentre helpers de tempo (`now_utc()`) para não reintroduzir o padrão antigo.

---

## RP-12 · Logger estruturado (AP-12) e constantes nomeadas (AP-13)

**Antes:**
```python
print("ERRO: " + str(e))
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`)  # vaza segredo!
```
**Depois:**
```python
import logging
logger = logging.getLogger(__name__)
logger.error("falha ao criar produto", exc_info=True)   # sem dados sensíveis
```
```python
VALID_STATUSES = ("pending", "in_progress", "done", "cancelled")
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
```
Nunca logar cartão, senha ou chave. Troque nomes crípticos (`u`, `eml`, `cc`) por
nomes descritivos (`user_name`, `email`, `card_number`).

---

## Sequência recomendada na Fase 3
1. Config/segredos (RP-01) → 2. Segurança de dados: SQL param + senha + endpoint
perigoso (RP-02, RP-03, RP-04) → 3. Estrutura em camadas (RP-05, RP-07) →
4. Regra de negócio para services (RP-06, RP-08) → 5. Performance e validação
(RP-09, RP-10) → 6. Deprecated + logging + nomes (RP-11, RP-12) → 7. **Validar**
boot + endpoints.
