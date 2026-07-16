// Controller de Relatório — agrega o resultado da query única (sem N+1/race).
module.exports = function reportController(deps) {
  const { payments, payment } = deps;

  return {
    async financialReport(req, res, next) {
      try {
        const rows = await payments.financialReportRows();
        const byCourse = new Map();

        for (const row of rows) {
          if (!byCourse.has(row.course_id)) {
            byCourse.set(row.course_id, { course: row.course, revenue: 0, students: [] });
          }
          const data = byCourse.get(row.course_id);
          if (row.enrollment_id !== null) {
            if (row.status === payment.PaymentStatus.PAID) {
              data.revenue += row.paid || 0;
            }
            data.students.push({
              student: row.student || 'Unknown',
              paid: row.paid || 0,
            });
          }
        }

        return res.json([...byCourse.values()]);
      } catch (err) {
        next(err);
      }
    },
  };
};
