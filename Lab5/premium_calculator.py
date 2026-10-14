
"""Insurance premium calculator for the Lab 5 assignment."""

import math
import os
import secrets
import tarfile
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

from defusedxml import ElementTree as ET


BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}
PROJECT_DIR = Path(__file__).resolve().parent
LOG_FILE = Path(
    os.environ.get(
        "LAB5_LOG_FILE",
        str(PROJECT_DIR / "premium_quotes.log"),
    )
)
CLAIMS_DIRECTORY = PROJECT_DIR / "claims_docs"
HOST = "127.0.0.1"
UNDERWRITER_TOKEN = os.environ.get("LAB5_UNDERWRITER_TOKEN", "")
quotes = {}


def calculate_premium(policy_type, customer, discounts=None):
    """Calculate a premium from policy, customer, and discount details."""
    if policy_type not in BASE_RATES:
        raise ValueError("Unsupported policy type.")

    required_fields = {"age", "sum_insured", "smoker", "claims"}
    if not isinstance(customer, dict) or not required_fields.issubset(customer):
        raise ValueError("Customer details are incomplete.")

    age = customer["age"]
    sum_insured = customer["sum_insured"]
    smoker = customer["smoker"]
    claims = customer["claims"]

    if not isinstance(age, int) or age < 0:
        raise ValueError("Age must be a nonnegative integer.")
    if not isinstance(sum_insured, (int, float)) or sum_insured < 0:
        raise ValueError("Sum insured must be nonnegative.")
    if not isinstance(claims, int) or claims < 0:
        raise ValueError("Claims must be a nonnegative integer.")
    if not isinstance(smoker, bool):
        raise ValueError("Smoker must be True or False.")

    applied_discounts = [] if discounts is None else list(discounts)
    premium = BASE_RATES[policy_type] + sum_insured * 0.002

    if age > 45:
        premium *= 1.5
    if smoker:
        premium *= 1.3

    premium += claims * 1000

    for discount in applied_discounts:
        if not isinstance(discount, (int, float)):
            raise ValueError("Discounts must be numeric.")
        if not math.isfinite(discount) or discount < 0:
            raise ValueError("Discounts must be finite and nonnegative.")
        premium -= discount

    return max(0.0, premium)


def age_from_dob(dob):
    """Calculate age from a date formatted as DD-MM-YYYY."""
    birth_date = datetime.strptime(dob, "%d-%m-%Y").date()
    today = date.today()

    if birth_date > today:
        raise ValueError("Date of birth cannot be in the future.")

    birthday_not_reached = (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    return today.year - birth_date.year - birthday_not_reached


def policy_number():
    """Generate a six-digit policy reference."""
    return f"POL-{secrets.randbelow(900000) + 100000}"


def save_quote(name, premium):
    """Store a quote in memory and append it to the quote log."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Customer name cannot be empty.")
    if not isinstance(premium, (int, float)):
        raise ValueError("Premium must be numeric.")
    if not math.isfinite(premium) or premium < 0:
        raise ValueError("Premium must be finite and nonnegative.")

    number = policy_number()
    quotes[number] = {"name": name, "premium": premium}
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("a", encoding="utf-8") as quote_file:
        quote_file.write(f"{number},{name},{premium:.2f}\n")

    return number


def parse_policy(policy):
    """Parse one policy element or return None when its data is invalid."""
    try:
        policy_type = policy.get("type")
        age = int(policy.get("age", ""))
        sum_insured = int(policy.get("sum", ""))
    except (TypeError, ValueError):
        return None

    if policy_type not in BASE_RATES or age < 0 or sum_insured < 0:
        return None

    return policy_type, age, sum_insured


def import_policies(xml_text):
    """Import valid policy records from XML input."""
    root = ET.fromstring(xml_text)
    result = []

    for policy in root.findall("policy"):
        parsed_policy = parse_policy(policy)
        if parsed_policy is not None:
            result.append(parsed_policy)

    return result


def fetch_rates(url):
    """Download rate data from an HTTPS URL with a timeout."""
    parsed_url = urlsplit(url)

    if parsed_url.scheme != "https" or not parsed_url.hostname:
        raise ValueError("Rate downloads require a valid HTTPS URL.")
    if parsed_url.username or parsed_url.password:
        raise ValueError("Credentials in URLs are not allowed.")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Lab5-InsuranceCalculator/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status != 200:
                raise RuntimeError("Unexpected HTTP response status.")
            return response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("Unable to download rate data.") from exc


def import_claim_documents(archive_path):
    """Extract claim documents using Python's safe archive data filter."""
    destination = CLAIMS_DIRECTORY.resolve()
    destination.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, mode="r:*") as archive:
        archive.extractall(path=destination, filter="data")


def monthly_instalment(premium, months=12):
    """Calculate the whole-number monthly instalment."""
    if not isinstance(premium, (int, float)):
        raise ValueError("Premium must be numeric.")
    if not math.isfinite(premium) or premium < 0:
        raise ValueError("Premium must be finite and nonnegative.")
    if not isinstance(months, int) or months <= 0:
        raise ValueError("Months must be a positive integer.")

    return math.floor(premium / months)


def is_authorised(token):
    """Check a token against the configured underwriter secret."""
    return (
        bool(UNDERWRITER_TOKEN)
        and isinstance(token, str)
        and secrets.compare_digest(token, UNDERWRITER_TOKEN)
    )


def renewal_due(start, years=1):
    """Calculate the renewal date, including leap-day boundaries."""
    if not isinstance(years, int) or years < 0:
        raise ValueError("Renewal years must be a nonnegative integer.")

    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    target_year = start_date.year + years

    try:
        renewal_date = start_date.replace(year=target_year)
    except ValueError:
        renewal_date = start_date.replace(
            year=target_year,
            month=2,
            day=28,
        )

    return renewal_date.isoformat()


def print_quotes():
    """Print all quotes currently held in memory."""
    print("===== Quote Book =====")

    for index, (number, quote) in enumerate(quotes.items(), start=1):
        print(
            index,
            number,
            quote["name"],
            "Rs.",
            f'{quote["premium"]:.2f}',
        )


def main():
    """Run demonstration cases for the calculator."""
    health_customer = {
        "age": 30,
        "sum_insured": 500000,
        "smoker": False,
        "claims": 0,
    }
    motor_customer = {
        "age": 50,
        "sum_insured": 800000,
        "smoker": False,
        "claims": 0,
    }
    life_customer = {
        "age": 25,
        "sum_insured": 100000,
        "smoker": False,
        "claims": 0,
    }

    premium_one = calculate_premium("health", health_customer)
    premium_two = calculate_premium("health", health_customer)
    motor_premium = calculate_premium("motor", motor_customer)
    life_premium = calculate_premium(
        "life",
        life_customer,
        [3000, 3000, 3000],
    )

    print("Quote 1:", premium_one)
    print("Quote 2 (same customer details):", premium_two)
    print("Non-smoker aged 50:", motor_premium)
    print("Life with stacked discounts:", life_premium)
    print("Age from DOB 31-12-1990:", age_from_dob("31-12-1990"))
    print("Monthly instalment:", monthly_instalment(motor_premium))
    print("Renewal due:", renewal_due("2025-03-15"))

    sample_xml = (
        "<policies>"
        "<policy type='health' age='40' sum='300000'/>"
        "<policy type='motor' age='abc' sum='1'/>"
        "</policies>"
    )
    print("Imported:", import_policies(sample_xml))

    quote_id = save_quote("Kiran", premium_one)
    print("Saved as:", quote_id)
    print("Authorised:", is_authorised(UNDERWRITER_TOKEN))
    print("Server would listen on", HOST)
    print_quotes()


if __name__ == "__main__":
    main()
