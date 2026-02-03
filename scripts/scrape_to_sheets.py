#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone

import gspread
import requests
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials


def load_urls(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip() and not line.startswith("#")]


def fetch_page(url: str, timeout: int = 20) -> dict[str, str]:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "HiScraper/1.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "").strip() if description_tag else ""
    return {
        "url": url,
        "title": title,
        "description": description,
        "status": str(response.status_code),
    }


def open_sheet(sheet_id: str, creds_json: dict) -> gspread.Worksheet:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(creds_json, scopes=scopes)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(sheet_id)
    return sheet.sheet1


def main() -> int:
    urls_path = os.environ.get("SCRAPE_URLS_FILE", "urls.txt")
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    creds_raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

    if not sheet_id:
        print("Missing GOOGLE_SHEET_ID environment variable.", file=sys.stderr)
        return 1
    if not creds_raw:
        print("Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable.", file=sys.stderr)
        return 1
    if not os.path.exists(urls_path):
        print(f"URLs file not found: {urls_path}", file=sys.stderr)
        return 1

    creds_json = json.loads(creds_raw)
    urls = load_urls(urls_path)
    if not urls:
        print("No URLs found to scrape.", file=sys.stderr)
        return 1

    worksheet = open_sheet(sheet_id, creds_json)
    timestamp = datetime.now(timezone.utc).isoformat()

    rows = [
        [
            "timestamp",
            "url",
            "title",
            "description",
            "status",
        ]
    ]

    for url in urls:
        data = fetch_page(url)
        rows.append([
            timestamp,
            data["url"],
            data["title"],
            data["description"],
            data["status"],
        ])

    worksheet.clear()
    worksheet.update(rows)
    print(f"Updated {len(rows) - 1} rows in Google Sheet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
