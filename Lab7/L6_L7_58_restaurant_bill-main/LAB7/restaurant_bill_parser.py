
def clean_dish_name(name):
    """
    Removes the chef's-special markers (*, #, ~) and title-cases the name.
    Returns an empty string for inputs that are not strings.
    """
    if not isinstance(name, str):
        return ""

    name = name.strip()
    for ch in ["*", "#", "~"]:
        name = name.replace(ch, "")
    return name.title()


def parse_item_prices(text):
    """
    Parses comma-separated, non-negative whole-number prices.
    Returns an empty list if the input is invalid.
    """
    if not isinstance(text, str):
        return []

    text = text.strip()
    if not text:
        return []

    prices = []
    for value in text.split(","):
        value = value.strip()

        if not value or not value.isdecimal():
            return []

        try:
            price = int(value)
        except (ValueError, TypeError):
            return []

        if price < 0:
            return []

        prices.append(price)

    return prices


def split_amount(text):
    """
    Splits TOTAL/PEOPLE and returns the whole-number share.
    Returns 0 for malformed input, negative totals, or non-positive people.
    """
    if not isinstance(text, str):
        return 0

    parts = text.split("/")
    if len(parts) != 2:
        return 0

    try:
        total = int(parts[0].strip())
        people = int(parts[1].strip())
    except (ValueError, TypeError):
        return 0

    if total < 0 or people <= 0:
        return 0

    return total // people


def main():
    print("==== Running clean_dish_name ====")
    value = input("Enter a dish name from the menu (e.g. *paneer tikka*): ")
    print("Dish name:", clean_dish_name(value))

    print("\n==== Running parse_item_prices ====")
    value = input("Enter item prices separated by commas (e.g. 250,180,320): ")
    print("Item prices:", parse_item_prices(value))

    print("\n==== Running split_amount ====")
    value = input("Enter the bill and number of people as TOTAL/PEOPLE (e.g. 1200/4): ")
    print("Each person pays:", split_amount(value))


if __name__ == "__main__":
    main()
