"""Compare documentation-only IP strings with IOC strings; never inspect live HTTP rows."""

DOCUMENTATION_CASES = {
    "match": {"ip": "198.51.100.20", "indicators": ["203.0.113.7", "198.51.100.20"]},
    "no_match": {"ip": "192.0.2.10", "indicators": ["203.0.113.7", "198.51.100.20"]},
}


def ioc_matches(ip, indicators):
    return ip in indicators


def main():
    for name, case in DOCUMENTATION_CASES.items():
        print(f"{name}: ip={case['ip']} indicators={case['indicators']} match={ioc_matches(case['ip'], case['indicators'])}")


if __name__ == "__main__":
    main()
