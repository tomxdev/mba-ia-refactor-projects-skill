// Model de Usuário — queries parametrizadas, nunca retorna o hash da senha.
module.exports = function userModel(db) {
  return {
    findByEmail(email) {
      return db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
    },
    async create(name, email, passHash) {
      const { lastID } = await db.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        [name, email, passHash]
      );
      return lastID;
    },
    delete(id) {
      return db.run('DELETE FROM users WHERE id = ?', [id]);
    },
  };
};
