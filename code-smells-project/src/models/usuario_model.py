"""Model de Usuário — hashing forte de senha; nunca serializa a senha."""
from werkzeug.security import check_password_hash, generate_password_hash


def _public(row):
    """Representação pública: NUNCA inclui o campo senha."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"] if "criado_em" in row.keys() else None,
    }


class UsuarioModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM usuarios")
        return [_public(r) for r in cursor.fetchall()]

    def get_by_id(self, usuario_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return _public(row) if row else None

    def create(self, nome, email, senha, tipo="cliente"):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, generate_password_hash(senha), tipo),
        )
        self.db.commit()
        return cursor.lastrowid

    def authenticate(self, email, senha):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row and check_password_hash(row["senha"], senha):
            return _public(row)
        return None
