"""
api_fetcher.py
---------------
Week 4, Tuesday: "APIs, HTTP requests and data processing"

What it does:
1. Makes an HTTP GET request to a public API (no key required).
2. Handles common failure modes safely: network errors, timeouts,
   and bad HTTP status codes.
3. Processes the JSON response into a simpler structure your reporting
   module can use.

Uses only 'urllib' (built into Python) so there's nothing extra to
install. If you'd rather use the 'requests' library, the same logic
applies — just swap urllib.request calls for requests.get().

Usage:
    python api_fetcher.py
"""

import json
import urllib.request
import urllib.error


class APIFetcher:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

    def fetch(self, endpoint: str = "") -> dict:
        """
        Fetches JSON data from base_url + endpoint.
        Returns a dict with 'success', 'data' (or 'error').
        """
        url = self.base_url + endpoint
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                if response.status != 200:
                    return {"success": False, "error": f"HTTP {response.status}"}
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
                return {"success": True, "data": data}

        except urllib.error.HTTPError as e:
            return {"success": False, "error": f"HTTP error: {e.code} {e.reason}"}
        except urllib.error.URLError as e:
            return {"success": False, "error": f"Network error: {e.reason}"}
        except json.JSONDecodeError:
            return {"success": False, "error": "Response was not valid JSON"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {e}"}


def process_public_holidays(data: list) -> dict:
    """
    Example processor: takes a list of public-holiday records from
    an API and summarises them. Swap this for whatever processing
    your chosen API's data actually needs.
    """
    if not isinstance(data, list):
        return {"count": 0, "names": []}
    return {
        "count": len(data),
        "names": [item.get("name", "Unknown") for item in data[:10]],  # first 10
    }


if __name__ == "__main__":
    # Example: public holidays API — no API key needed, good for testing.
    # https://date.nager.at/Api
    fetcher = APIFetcher("https://date.nager.at/api/v3")
    result = fetcher.fetch("/PublicHolidays/2026/ZA")

    if result["success"]:
        summary = process_public_holidays(result["data"])
        print(f"Fetched {summary['count']} public holidays for South Africa (2026):")
        for name in summary["names"]:
            print(f"  - {name}")
    else:
        print(f"Could not fetch data: {result['error']}")
