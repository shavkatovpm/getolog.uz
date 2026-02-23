from core.bot_manager import _make_webhook_secret


class TestWebhookSecret:
    def test_secret_is_deterministic(self):
        token = "123456:ABC-DEF1234"
        s1 = _make_webhook_secret(token)
        s2 = _make_webhook_secret(token)
        assert s1 == s2

    def test_secret_does_not_contain_token(self):
        token = "123456:ABC-DEF1234"
        secret = _make_webhook_secret(token)
        assert "123456" not in secret
        assert "ABC-DEF" not in secret

    def test_secret_is_32_chars(self):
        token = "123456:ABC-DEF1234"
        secret = _make_webhook_secret(token)
        assert len(secret) == 32

    def test_different_tokens_different_secrets(self):
        s1 = _make_webhook_secret("111:aaa")
        s2 = _make_webhook_secret("222:bbb")
        assert s1 != s2

    def test_secret_is_hex(self):
        secret = _make_webhook_secret("123:test")
        assert all(c in "0123456789abcdef" for c in secret)
