from __future__ import annotations

import logging

from cryptography.fernet import Fernet

from bot.config import DATA_DIR, config

logger = logging.getLogger(__name__)

# Ключ, вшитый в код: бот стартует даже без ENCRYPTION_KEY и без secret.key.
# Свой ключ можно задать через ENCRYPTION_KEY (строка из 44 символов base64) —
# но данные, зашифрованные с другим ключом, после смены не расшифруются.
_DEFAULT_KEY = b"Bct_1aJfA8PVEnhpBOk-PXbilqyqsH793XPGlWWReKg="


def _is_fernet_key(value: bytes) -> bool:
    try:
        Fernet(value)
        return True
    except Exception:
        return False


def _load_key() -> bytes:
    env = config.encryption_key.strip()
    if env:
        if _is_fernet_key(env.encode()):
            return env.encode()
        logger.warning("ENCRYPTION_KEY задан, но это не ключ Fernet — игнорирую и использую запасной")

    path = DATA_DIR / "secret.key"
    try:
        if path.exists():
            key = path.read_bytes().strip()
            if _is_fernet_key(key):
                return key
            logger.warning("Файл %s повреждён — заменяю вшитым ключом", path)
    except OSError:
        logger.warning("Не удалось прочитать %s — использую вшитый ключ", path)

    try:
        path.write_bytes(_DEFAULT_KEY)
    except OSError:
        pass
    return _DEFAULT_KEY


_fernet = Fernet(_load_key())


def encrypt(value: str) -> str:
    return _fernet.encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return _fernet.decrypt(value.encode()).decode()
