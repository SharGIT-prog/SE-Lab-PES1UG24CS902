
from hypothesis import given, settings, strategies as st
from restaurant_bill_parser import (
    clean_dish_name,
    parse_item_prices,
    split_amount,
)


fuzz_inputs = st.one_of(
    st.text(),
    st.none(),
    st.integers(),
    st.floats(allow_nan=True, allow_infinity=True),
    st.booleans(),
    st.lists(st.text()),
)


@settings(max_examples=200, deadline=None)
@given(fuzz_inputs)
def test_clean_dish_name_no_crash(value):
    try:
        result = clean_dish_name(value)
    except Exception as exc:
        assert False, f"clean_dish_name crashed with {value!r}: {exc}"

    assert isinstance(result, str)


@settings(max_examples=200, deadline=None)
@given(fuzz_inputs)
def test_parse_item_prices_no_crash(value):
    try:
        result = parse_item_prices(value)
    except Exception as exc:
        assert False, f"parse_item_prices crashed with {value!r}: {exc}"

    assert isinstance(result, list)
    assert all(isinstance(price, int) and price >= 0 for price in result)


@settings(max_examples=200, deadline=None)
@given(fuzz_inputs)
def test_split_amount_no_crash(value):
    try:
        result = split_amount(value)
    except Exception as exc:
        assert False, f"split_amount crashed with {value!r}: {exc}"

    assert isinstance(result, int)
    assert result >= 0
