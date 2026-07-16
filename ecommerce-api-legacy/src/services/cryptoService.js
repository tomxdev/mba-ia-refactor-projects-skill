// Hashing forte de senha com scrypt nativo do Node (substitui o badCrypto caseiro).
const crypto = require('crypto');

const KEYLEN = 64;

function hashPassword(password) {
  return new Promise((resolve, reject) => {
    const salt = crypto.randomBytes(16).toString('hex');
    crypto.scrypt(password, salt, KEYLEN, (err, derivedKey) => {
      if (err) return reject(err);
      resolve(`${salt}:${derivedKey.toString('hex')}`);
    });
  });
}

function verifyPassword(password, stored) {
  return new Promise((resolve, reject) => {
    const [salt, key] = String(stored).split(':');
    if (!salt || !key) return resolve(false);
    crypto.scrypt(password, salt, KEYLEN, (err, derivedKey) => {
      if (err) return reject(err);
      const keyBuffer = Buffer.from(key, 'hex');
      resolve(
        keyBuffer.length === derivedKey.length &&
          crypto.timingSafeEqual(keyBuffer, derivedKey)
      );
    });
  });
}

module.exports = { hashPassword, verifyPassword };
