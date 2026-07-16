// Routes — apenas mapeiam método+caminho → handler do controller.
const express = require('express');

module.exports = function buildRouter({ checkout, report, user }) {
  const router = express.Router();

  router.post('/api/checkout', checkout.checkout);
  router.get('/api/admin/financial-report', report.financialReport);
  router.delete('/api/users/:id', user.deleteUser);

  return router;
};
