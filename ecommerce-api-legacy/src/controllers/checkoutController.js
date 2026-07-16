// Controller de Checkout — fluxo linear com async/await + transação (era callback hell).
module.exports = function checkoutController(deps) {
  const { db, users, courses, enrollments, payments, crypto, payment } = deps;

  return {
    async checkout(req, res, next) {
      try {
        const { usr, eml, pwd, c_id: courseId, card } = req.body;

        if (!usr || !eml || !courseId || !card) {
          return res.status(400).send('Bad Request');
        }

        const course = await courses.findActiveById(courseId);
        if (!course) return res.status(404).send('Curso não encontrado');

        const status = payment.authorize(card);
        if (status === payment.PaymentStatus.DENIED) {
          return res.status(400).send('Pagamento recusado');
        }

        const enrollmentId = await db.transaction(async () => {
          let user = await users.findByEmail(eml);
          const userId = user
            ? user.id
            : await users.create(usr, eml, await crypto.hashPassword(pwd || '123456'));

          const newEnrollmentId = await enrollments.create(userId, courseId);
          await payments.create(newEnrollmentId, course.price, status);
          await db.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [`Checkout curso ${courseId} por ${userId}`]
          );
          return newEnrollmentId;
        });

        return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
      } catch (err) {
        next(err);
      }
    },
  };
};
