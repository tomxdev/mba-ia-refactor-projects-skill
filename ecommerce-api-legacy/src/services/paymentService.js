// Regra de autorização de pagamento — isolada, sem logar dados sensíveis.
const APPROVED_CARD_PREFIX = '4';

const PaymentStatus = { PAID: 'PAID', DENIED: 'DENIED' };

function authorize(cardNumber) {
  // Mantém a regra original (cartão iniciado em "4" é aprovado) sem expor
  // número do cartão nem chave do gateway em logs.
  return cardNumber && String(cardNumber).startsWith(APPROVED_CARD_PREFIX)
    ? PaymentStatus.PAID
    : PaymentStatus.DENIED;
}

module.exports = { authorize, PaymentStatus };
