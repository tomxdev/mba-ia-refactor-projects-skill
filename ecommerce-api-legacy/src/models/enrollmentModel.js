// Model de Matrícula.
module.exports = function enrollmentModel(db) {
  return {
    async create(userId, courseId) {
      const { lastID } = await db.run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, courseId]
      );
      return lastID;
    },
    idsByUser(userId) {
      return db
        .all('SELECT id FROM enrollments WHERE user_id = ?', [userId])
        .then((rows) => rows.map((r) => r.id));
    },
    deleteByUser(userId) {
      return db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    },
  };
};
