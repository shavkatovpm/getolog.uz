from utils.constants import PaymentStatus, PlanName, SubStatus


class TestPaymentStatus:
    def test_values(self):
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.APPROVED == "approved"
        assert PaymentStatus.REJECTED == "rejected"

    def test_string_comparison(self):
        assert PaymentStatus.PENDING == "pending"
        assert "approved" == PaymentStatus.APPROVED


class TestPlanName:
    def test_values(self):
        assert PlanName.FREE == "free"
        assert PlanName.STANDARD == "standard"
        assert PlanName.PREMIUM == "premium"

    def test_dict_key_lookup(self):
        plans = {PlanName.FREE: "bepul", PlanName.STANDARD: "standart"}
        assert plans["free"] == "bepul"
        assert plans[PlanName.FREE] == "bepul"


class TestSubStatus:
    def test_values(self):
        assert SubStatus.ACTIVE == "active"
        assert SubStatus.EXPIRED == "expired"
        assert SubStatus.KICKED == "kicked"

    def test_string_comparison(self):
        assert SubStatus.ACTIVE == "active"
        assert "expired" == SubStatus.EXPIRED
