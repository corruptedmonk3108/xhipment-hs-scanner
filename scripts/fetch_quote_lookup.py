import csv
import io
import json
import sys

import requests

SHEET_ID = "1Y_uaf3ZZYwCcakTKMFwF1p859xaVV2f1y4nVPadEM5U"
SHEET_NAME = "Upcoming Shipments"

url = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/gviz/tq?tqx=out:csv&sheet={SHEET_NAME.replace(' ', '+')}"
)

try:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
except requests.RequestException as e:
    print(f"ERROR: Failed to fetch sheet — {e}", file=sys.stderr)
    print("Make sure the Google Sheet is shared as 'Anyone with the link can view'.", file=sys.stderr)
    sys.exit(1)

if "<html" in r.text[:200].lower():
    print("ERROR: Got an HTML response instead of CSV. The sheet may not be publicly accessible.", file=sys.stderr)
    print("Share the sheet as 'Anyone with the link can view' and try again.", file=sys.stderr)
    sys.exit(1)

reader = csv.reader(io.StringIO(r.text))
rows = list(reader)

if not rows:
    print("ERROR: Sheet returned no data.", file=sys.stderr)
    sys.exit(1)

# Column A (index 0) = QuoteId, Column C (index 2) = ExportsInvoiceValue, Column E (index 4) = url
results = []
for i, row in enumerate(rows[1:], start=2):
    if len(row) < 3:
        continue
    quote_id = row[0].strip()
    raw_value = row[2].strip().replace(",", "")
    shipper = row[3].strip() if len(row) > 3 and row[3] else ""
    url = row[4].strip() if len(row) > 4 and row[4] else ""
    if not quote_id:
        continue
    try:
        val = float(raw_value)
    except ValueError:
        continue
    results.append({"quoteId": quote_id, "exportsInvoiceValue": val, "shipper": shipper, "url": url})

with open("quote_lookup.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"Done: {len(results)} entries written to quote_lookup.json")
