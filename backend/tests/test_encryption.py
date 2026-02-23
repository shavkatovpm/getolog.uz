from core.encryption import encrypt_token, decrypt_token, encrypt_card, decrypt_card


class TestTokenEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        encrypted = encrypt_token(token)
        assert encrypted != token
        assert decrypt_token(encrypted) == token

    def test_encrypted_is_different_each_time(self):
        token = "123456:test"
        e1 = encrypt_token(token)
        e2 = encrypt_token(token)
        assert e1 != e2
        assert decrypt_token(e1) == token
        assert decrypt_token(e2) == token


class TestCardEncryption:
    def test_encrypt_decrypt_card(self):
        card = "8600 1402 3105 3871"
        encrypted = encrypt_card(card)
        assert encrypted != card
        assert decrypt_card(encrypted) == card

    def test_decrypt_legacy_plain_text(self):
        plain = "8600 1402 3105 3871"
        assert decrypt_card(plain) == plain
