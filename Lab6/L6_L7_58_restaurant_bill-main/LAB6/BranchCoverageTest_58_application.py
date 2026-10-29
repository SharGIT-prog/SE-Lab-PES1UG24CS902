"""Branch coverage tests for restaurant_bill.py (Lab 6)."""
import pytest
from restaurant_bill import bill_total, split_bill, table_wait


@pytest.mark.parametrize(
    "section,food,guests,happy,expected",
    [
        ("dine_in", 1000, 2, False, 1155),  # no discount, no surcharge
        ("dine_in", 1000, 2, True, 924),    # happy-hour discount
        ("takeaway", 500, 2, True, 525),    # takeaway excluded from discount
        ("rooftop", 1000, 8, True, 1176),   # rooftop + discount + surcharge
        ("rooftop", 100, 7, False, 120),    # no surcharge at 7 guests
    ],
)
def test_bill_decision_branches(section, food, guests, happy, expected):
    assert bill_total(section, food, guests, happy) == expected


@pytest.mark.parametrize("section", ["unknown", "", None])
def test_bill_unknown_section_branch(section):
    with pytest.raises(ValueError, match="unknown section"):
        bill_total(section, 100, 1, False)


@pytest.mark.parametrize(
    "food,guests",
    [(-1, 1), (100, 0), (-1, 0), (0, 1)],
)
def test_bill_validation_branches(food, guests):
    if food < 0 or guests < 1:
        with pytest.raises(ValueError, match="invalid order"):
            bill_total("dine_in", food, guests, False)
    else:
        assert bill_total("dine_in", food, guests, False) == 0


@pytest.mark.parametrize(
    "total,people,tip,expected",
    [
        (1000, 4, 10, 275),  # divisible evenly
        (101, 2, 10, 56),    # remainder causes round-up
        (0, 3, 0, 0),        # no remainder
    ],
)
def test_split_bill_remainder_branches(total, people, tip, expected):
    assert split_bill(total, people, tip) == expected


@pytest.mark.parametrize("people", [0, -1])
def test_split_bill_invalid_people_branch(people):
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(100, people, 0)


@pytest.mark.parametrize("tip", [-1, -10])
def test_split_bill_invalid_tip_branch(tip):
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(100, 2, tip)


@pytest.mark.parametrize(
    "party,tables,reservation,expected",
    [
        (13, 5, False, "call ahead"),  # oversized party
        (13, 5, True, "call ahead"),   # oversized check precedes reservation
        (4, 0, True, "seat now"),      # reservation precedes table checks
        (4, 0, False, "waitlist"),     # no tables
        (7, 1, False, "waitlist"),     # large party, fewer than 2 tables
        (7, 2, False, "seat now"),     # large party, enough tables
        (6, 1, False, "seat now"),     # party size is not greater than 6
        (4, 1, False, "seat now"),     # ordinary available table
    ],
)
def test_table_wait_all_decision_branches(party, tables, reservation, expected):
    assert table_wait(party, tables, reservation) == expected
