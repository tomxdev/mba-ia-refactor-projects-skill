// Camada de acesso com API baseada em Promises (elimina o callback hell) + schema/seed.
//
// Driver resiliente: usa o pacote `sqlite3` (dependência declarada). Se o binário
// nativo não estiver disponível no ambiente, cai para o `node:sqlite` embutido
// (Node >= 22), mantendo a mesma interface assíncrona.
const crypto = require('./services/cryptoService');

function createDriver(path) {
  try {
    const sqlite3 = require('sqlite3').verbose();
    const db = new sqlite3.Database(path);
    return {
      name: 'sqlite3',
      run: (sql, p = []) =>
        new Promise((resolve, reject) => {
          db.run(sql, p, function (err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
          });
        }),
      get: (sql, p = []) =>
        new Promise((resolve, reject) =>
          db.get(sql, p, (err, row) => (err ? reject(err) : resolve(row)))
        ),
      all: (sql, p = []) =>
        new Promise((resolve, reject) =>
          db.all(sql, p, (err, rows) => (err ? reject(err) : resolve(rows)))
        ),
    };
  } catch (_) {
    const { DatabaseSync } = require('node:sqlite');
    const db = new DatabaseSync(path);
    const num = (v) => (typeof v === 'bigint' ? Number(v) : v);
    return {
      name: 'node:sqlite',
      run: (sql, p = []) => {
        const r = db.prepare(sql).run(...p);
        return Promise.resolve({ lastID: num(r.lastInsertRowid), changes: num(r.changes) });
      },
      get: (sql, p = []) => Promise.resolve(db.prepare(sql).get(...p)),
      all: (sql, p = []) => Promise.resolve(db.prepare(sql).all(...p)),
    };
  }
}

class Database {
  constructor(path = ':memory:') {
    this.driver = createDriver(path);
  }

  run(sql, params = []) {
    return this.driver.run(sql, params);
  }

  get(sql, params = []) {
    return this.driver.get(sql, params);
  }

  all(sql, params = []) {
    return this.driver.all(sql, params);
  }

  // Sequência de operações atômica (garante integridade no checkout/deleção).
  async transaction(work) {
    await this.run('BEGIN');
    try {
      const result = await work();
      await this.run('COMMIT');
      return result;
    } catch (e) {
      await this.run('ROLLBACK');
      throw e;
    }
  }

  async init() {
    await this.run(
      'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pass TEXT)'
    );
    await this.run(
      'CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)'
    );
    await this.run(
      'CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)'
    );
    await this.run(
      'CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)'
    );
    await this.run(
      'CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)'
    );

    const seeded = await this.get('SELECT COUNT(*) AS n FROM users');
    if (seeded.n === 0) {
      const hash = await crypto.hashPassword('123');
      await this.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        'Leonan',
        'leonan@fullcycle.com.br',
        hash,
      ]);
      await this.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
        ['Clean Architecture', 997.0, 'Docker', 497.0]
      );
      await this.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
      await this.run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')"
      );
    }
  }
}

module.exports = Database;
