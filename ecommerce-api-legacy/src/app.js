// Composition root — cria app, injeta dependências e sobe o servidor.
const express = require('express');
const config = require('./config');
const Database = require('./database');
const cryptoService = require('./services/cryptoService');
const paymentService = require('./services/paymentService');
const userModel = require('./models/userModel');
const courseModel = require('./models/courseModel');
const enrollmentModel = require('./models/enrollmentModel');
const paymentModel = require('./models/paymentModel');
const checkoutController = require('./controllers/checkoutController');
const reportController = require('./controllers/reportController');
const userController = require('./controllers/userController');
const buildRouter = require('./routes');
const errorHandler = require('./middlewares/errorHandler');

async function createApp() {
  const db = new Database(config.db.path);
  await db.init();

  const users = userModel(db);
  const courses = courseModel(db);
  const enrollments = enrollmentModel(db);
  const payments = paymentModel(db);

  const deps = {
    db,
    users,
    courses,
    enrollments,
    payments,
    crypto: cryptoService,
    payment: paymentService,
  };

  const app = express();
  app.use(express.json());
  app.use(
    buildRouter({
      checkout: checkoutController(deps),
      report: reportController(deps),
      user: userController(deps),
    })
  );
  app.use(errorHandler);

  return { app, db };
}

if (require.main === module) {
  createApp().then(({ app }) => {
    app.listen(config.port, () => {
      console.log(`LMS rodando na porta ${config.port}...`);
    });
  });
}

module.exports = createApp;
