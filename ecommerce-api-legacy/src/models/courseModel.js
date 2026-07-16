// Model de Curso.
module.exports = function courseModel(db) {
  return {
    findActiveById(id) {
      return db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
    },
    all() {
      return db.all('SELECT * FROM courses');
    },
  };
};
