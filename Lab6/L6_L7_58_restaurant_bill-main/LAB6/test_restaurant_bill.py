import pytest
from restaurant_bill import bill_total, split_bill, table_wait

#Example test cases:
def test_dine_in_bill():
    assert bill_total("dine_in", 1000, 2, False) == 1155

def test_even_split():
    assert split_bill(1000, 4, 10) == 275

#Write the rest of the test cases so that the code is 90- 100% covered.
