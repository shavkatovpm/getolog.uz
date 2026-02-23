from utils.validators import luhn_check, validate_card


class TestLuhnCheck:
    def test_valid_visa(self):
        assert luhn_check("4111111111111111") is True

    def test_invalid_checksum(self):
        assert luhn_check("4111111111111112") is False

    def test_too_short(self):
        assert luhn_check("411111111111") is False

    def test_all_zeros(self):
        assert luhn_check("0000000000000000") is True


class TestValidateCard:
    def test_uzcard_valid(self):
        result = validate_card("8600140231053871")
        assert result == "8600 1402 3105 3871"

    def test_humo_valid(self):
        result = validate_card("9860100125461718")
        assert result == "9860 1001 2546 1718"

    def test_uzcard_with_spaces(self):
        result = validate_card("8600 1402 3105 3871")
        assert result == "8600 1402 3105 3871"

    def test_international_valid_luhn(self):
        result = validate_card("4111111111111111")
        assert result == "4111 1111 1111 1111"

    def test_international_invalid_luhn(self):
        result = validate_card("4111111111111112")
        assert result is None

    def test_too_short(self):
        result = validate_card("860014023105")
        assert result is None

    def test_non_digits(self):
        result = validate_card("abcd1234efgh5678")
        assert result is None

    def test_empty(self):
        result = validate_card("")
        assert result is None
