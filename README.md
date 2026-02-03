# Hi Scraper Workflow

This repository contains a GitHub Actions workflow that scrapes a list of websites and writes the results into a Google Sheet.

## What it does

- Reads URLs from `urls.txt`.
- Fetches each page and extracts the page title and meta description.
- Writes the results into the first worksheet of a Google Sheet.

## Setup

1. Create a Google Sheet and copy its ID from the URL.
2. Create a Google Cloud service account with access to Google Sheets.
3. Share the Sheet with the service account email.
4. Add GitHub repository secrets:
   - `GOOGLE_SHEET_ID`: the Sheet ID.
   - `GOOGLE_SERVICE_ACCOUNT_JSON`: the full JSON key for the service account.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_SHEET_ID="your-sheet-id"
export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
python scripts/scrape_to_sheets.py
```

## Run on GitHub Actions

The workflow file is `.github/workflows/scrape_to_sheets.yml`. It runs:

- On a daily schedule at 07:00 UTC.
- Manually via the Actions tab (workflow_dispatch).

## Customize

- Update `urls.txt` with one URL per line.
- Adjust the cron schedule in the workflow file if needed.
