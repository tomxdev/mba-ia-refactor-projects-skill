// Model de Pagamento.
module.exports = function paymentModel(db) {
  return {
    create(enrollmentId, amount, status) {
      return db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, amount, status]
      );
    },
    deleteByEnrollmentIds(ids) {
      if (!ids.length) return Promise.resolve({ changes: 0 });
      const placeholders = ids.map(() => '?').join(',');
      return db.run(
        `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`,
        ids
      );
    },
    // Relatório financeiro em UMA query com JOINs (elimina o N+1 do original).
    financialReportRows() {
      return db.all(
        `SELECT c.id AS course_id, c.title AS course,
                e.id AS enrollment_id, u.name AS student,
                p.amount AS paid, p.status AS status
         FROM courses c
         LEFT JOIN enrollments e ON e.course_id = c.id
         LEFT JOIN users u ON u.id = e.user_id
         LEFT JOIN payments p ON p.enrollment_id = e.id
         ORDER BY c.id`
      );
    },
  };
};
