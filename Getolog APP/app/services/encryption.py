"""Bot tokenlarini bazada shifrlab saqlash/o'qish uchun yordamchi funksiyalar.

Token hech qachon bazaga ochiq matn holida yozilmaydi — faqat shu modul
orqali shifrlangan holda. Kalit ENCRYPTION_KEY (.env) da saqlanadi, bazaning
o'zida emas — shunda baza nusxasi o'g'irlansa ham tokenlar ochilmaydi.
"""

from cryptography.fernet import Fernet

from app.config import settings

_fernet = Fernet(settings.encryption_key.encode())


def encrypt_token(token: str) -> str:
    """Ochiq bot tokenini shifrlangan matnga aylantiradi (bazaga yozish uchun)."""
    return _fernet.encrypt(token.encode()).decode()


def decrypt_token(token_encrypted: str) -> str:
    """Bazadan o'qilgan shifrlangan tokenni ochiq holatga qaytaradi."""
    return _fernet.decrypt(token_encrypted.encode()).decode()
