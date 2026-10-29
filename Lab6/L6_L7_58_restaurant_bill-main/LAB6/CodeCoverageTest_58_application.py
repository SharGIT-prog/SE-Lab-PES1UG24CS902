"""Line/code coverage tests for restaurant_bill.py (Lab 6)."""
import pytest
from restaurant_bill import bill_total, split_bill, table_wait


def test_bill_dine_in_without_happy_hour():
    assert bill_total("dine_in", 1000, 2, False) == 1155


def test_bill_takeaway_happy_hour_does_not_discount():
    # Happy hour is ignored for takeaway.
    assert bill_total("takeaway", 500, 2, True) == 525


def test_bill_rooftop_happy_hour_and_large_party():
    # 1000 -> discounted food 800; service 120; party surcharge 200;
    # total 1120, then 5% tax = 1176.
    assert bill_total("rooftop", 1000, 8, True) == 1176


@pytest.mark.parametrize("section", ["unknown", "", None])
def test_unknown_section_raises(section):
    with pytest.raises(ValueError, match="unknown section"):
        bill_total(section, 100, 2, False)


@pytest.mark.parametrize(
    "section,food,guests",
    [("dine_in", -1, 2), ("dine_in", 100, 0), ("rooftop", -1, 0)],
)
def test_invalid_bill_inputs_raise(section, food, guests):
    with pytest.raises(ValueError, match="invalid order"):
        bill_total(section, food, guests, False)


def test_split_bill_even_division():
    assert split_bill(1000, 4, 10) == 275


def test_split_bill_rounds_up_remainder():
    # (101 + 10% tip) = 111; 111 / 2 rounds up to 56.
    assert split_bill(101, 2, 10) == 56


@pytest.mark.parametrize("people", [0, -1])
def test_split_bill_rejects_invalid_people(people):
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(100, people, 0)


@pytest.mark.parametrize("tip", [-1, -10])
def test_split_bill_rejects_negative_tip(tip):
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(100, 2, tip)


def test_table_wait_oversized_party():
    assert table_wait(13, 5, False) == "call ahead"


def test_table_wait_reservation_takes_priority():
    assert table_wait(4, 0, True) == "seat now"


def test_table_wait_no_free_tables():
    assert table_wait(4, 0, False) == "waitlist"


def test_table_wait_large_party_and_only_one_table():
    assert table_wait(7, 1, False) == "waitlist"


def test_table_wait_available_table():
    assert table_wait(4, 1, False) == "seat now"
