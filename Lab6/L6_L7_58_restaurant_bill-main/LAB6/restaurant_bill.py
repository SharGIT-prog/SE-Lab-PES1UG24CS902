SERVICE_CHARGE = {"dine_in": 10, "takeaway": 0, "rooftop": 15}


def bill_total(section, food_total, guests, is_happy_hour):
    if section not in SERVICE_CHARGE:
        raise ValueError("unknown section")
    if food_total < 0 or guests < 1:
        raise ValueError("invalid order")
    if is_happy_hour and section != "takeaway":
        food_total = food_total * 80 // 100
    service = food_total * SERVICE_CHARGE[section] // 100
    if guests >= 8:
        service += 200
    total = food_total + service
    return total + total * 5 // 100


def split_bill(total, people, tip_percent):
    if people < 1:
        raise ValueError("invalid people count")
    if tip_percent < 0:
        raise ValueError("invalid tip")
    grand_total = total + total * tip_percent // 100
    share = grand_total // people
    if grand_total % people != 0:
        share += 1
    return share


def table_wait(party_size, free_tables, has_reservation):
    if party_size > 12:
        return "call ahead"
    if has_reservation:
        return "seat now"
    if free_tables == 0:
        return "waitlist"
    elif party_size > 6 and free_tables < 2:
        return "waitlist"
    return "seat now"
