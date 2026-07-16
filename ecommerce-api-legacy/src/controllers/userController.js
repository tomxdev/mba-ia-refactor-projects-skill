// Controller de Usuário — deleção com integridade referencial (sem órfãos).
module.exports = function userController(deps) {
  const { db, users, enrollments, payments } = deps;

  return {
    async deleteUser(req, res, next) {
      try {
        const userId = req.params.id;
        await db.transaction(async () => {
          const enrollmentIds = await enrollments.idsByUser(userId);
          await payments.deleteByEnrollmentIds(enrollmentIds);
          await enrollments.deleteByUser(userId);
          await users.delete(userId);
        });
        return res.json({ msg: 'Usuário e dados relacionados removidos' });
      } catch (err) {
        next(err);
      }
    },
  };
};
