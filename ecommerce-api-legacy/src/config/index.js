// Configuração central — segredos vêm do ambiente, nunca hardcoded.
try {
  // Opcional: carrega .env se a dependência estiver disponível.
  require('dotenv').config();
} catch (_) {
  /* dotenv não instalado — usa variáveis de ambiente do processo. */
}

module.exports = {
  port: parseInt(process.env.PORT || '3000', 10),
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtpUser: process.env.SMTP_USER || '',
  db: {
    user: process.env.DB_USER || '',
    pass: process.env.DB_PASS || '',
    path: process.env.DB_PATH || ':memory:',
  },
};
