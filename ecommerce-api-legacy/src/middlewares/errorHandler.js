// Tratamento de erro centralizado (sem vazar dados sensíveis nos logs).
module.exports = function errorHandler(err, req, res, _next) {
  console.error('[ERRO]', err && err.message);
  res.status(500).json({ error: 'Erro interno' });
};
