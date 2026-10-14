
"""Insurance premium calculator."""

import math
import os
import secrets
import tarfile
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from defusedxml import ElementTree as ET


quotes = {}
HOST = "127.0.0.1"
UNDERWRITER_TOKEN = os.environ.get("LAB5_UNDERWRITER_TOKEN", "")
PROJECT_DIR = Path(__file__).resolve().parent
LOG_FILE = Path(
    os.environ.get("LAB5_LOG_FILE", str(PROJECT_DIR / "premium_quotes.log"))
)
BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}


def calculatePremium(
    policy_type, age, sum_insured, smoker, claims, discounts=[]
):
    """Calculate an insurance premium."""
    base = BASE_RATES[policy_type]
    premium = base + sum_insured * 0.002
    if age > 45:
        premium *= 1.5
    if smoker:
        premium *= 1.3
    premium += claims * 1000
    for discount in discounts:
        premium -= discount
    discounts.append(500)
    return premium


def ageFromDob(dob):
    """Calculate age from a date of birth."""
    born = datetime.strptime(dob, "%d-%m-%Y")
    today = datetime.now()
    return today.year - born.year


def policyNumber():
    """Generate a policy reference."""
    return f"POL-{secrets.randbelow(900000) + 100000}"


def saveQuote(name, premium):
    """Save a quote in memory and append it to the log."""
    number = policyNumber()
    quotes[number] = {"name": name, "premium": premium}
    with LOG_FILE.open("a", encoding="utf-8") as quote_file:
        quote_file.write(f"{number},{name},{premium:.2f}\n")
    return number


def importPolicies(xml_text):
    """Import policies from XML."""
    root = ET.fromstring(xml_text)
    result = []
    for policy in root.findall("policy"):
        try:
            result.append(
                (
                    policy.get("type"),
                    int(policy.get("age", "")),
                    int(policy.get("sum", "")),
                )
            )
        except (TypeError, ValueError):
            continue
    return result


def fetchRates(url):
    """Fetch rate data from an HTTPS URL."""
    parsed_url = urlsplit(url)
    if parsed_url.scheme != "https" or not parsed_url.hostname:
        raise ValueError("Only valid HTTPS URLs are allowed.")
    if parsed_url.username or parsed_url.password:
        raise ValueError("Credentials in URLs are not allowed.")

    request = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(  # nosec B310: HTTPS validated above.
            request, timeout=10
        ) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("Unable to fetch rates.") from exc


def importClaimDocuments(archive_path):
    """Safely extract claim documents."""
    destination = PROJECT_DIR / "claims_docs"
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, mode="r:*") as archive:
        archive.extractall(  # nosec B202: Python data filter is enabled.
            path=destination.resolve(), filter="data"
        )


def monthlyInstalment(premium, months=12):
    """Calculate a monthly instalment."""
    if months == 0:
        return premium
    else:
        return math.floor(premium / months)


def isAuthorised(token):
    """Check the underwriter token."""
    return secrets.compare_digest(token, UNDERWRITER_TOKEN)


def renewalDue(start, years=1):
    """Calculate the renewal date."""
    start_date = datetime.strptime(start, "%Y-%m-%d")
    return start_date.replace(
        year=start_date.year + years
    ).strftime("%Y-%m-%d")


def printQuotes():
    """Print the quote book."""
    print("===== Quote Book =====")
    keys = list(quotes.keys())
    for index in range(len(keys)):
        print(
            index + 1,
            keys[index],
            quotes[keys[index]]["name"],
            "Rs.",
            quotes[keys[index]]["premium"],
        )


def main():
    """Run sample insurance calculations."""
    premium_one = calculatePremium("health", 30, 500000, False, 0)
    premium_two = calculatePremium("health", 30, 500000, False, 0)
    motor_premium = calculatePremium("motor", 50, 800000, False, 0)
    life_premium = calculatePremium(
        "life", 25, 100000, False, 0, [3000, 3000, 3000]
    )
    print("Quote 1:", premium_one)
    print("Quote 2 (same customer details):", premium_two)
    print("Non-smoker aged 50:", motor_premium)
    print("Life with stacked discounts:", life_premium)
    print("Age from DOB 31-12-1990:", ageFromDob("31-12-1990"))
    print("Monthly instalment:", monthlyInstalment(motor_premium))
    print("Renewal due:", renewalDue("2025-03-15"))
    print(
        "Imported:",
        importPolicies(
            "<policies><policy type='health' age='40' sum='300000'/>"
            "<policy type='motor' age='abc' sum='1'/></policies>"
        ),
    )
    print("Saved as:", saveQuote("Kiran", premium_one))
    print("Authorised:", isAuthorised(UNDERWRITER_TOKEN))
    print("Server would listen on", HOST)
    printQuotes()


if __name__ == "__main__":
    main()

