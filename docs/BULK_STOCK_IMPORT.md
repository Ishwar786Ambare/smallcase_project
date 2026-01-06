# Bulk Stock Import via CSV/Excel

This feature allows you to bulk import stocks into your PostgreSQL database via the Django Admin interface using CSV or Excel files.

## Features

✅ **CSV and Excel Support** - Upload `.csv`, `.xlsx`, or `.xls` files  
✅ **Auto-fetch Stock Data** - Automatically fetches company name and current price from Yahoo Finance  
✅ **NSE & BSE Support** - Choose between NSE (.NS) or BSE (.BO) exchanges  
✅ **Smart Symbol Detection** - Automatically adds exchange suffix if not present  
✅ **Update Existing Stocks** - Updates stock information if already exists  
✅ **Detailed Reporting** - Shows count of created, updated, and failed imports  

---

## How to Use

### Step 1: Access Django Admin

1. Start your development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to: http://localhost:8000/admin/

3. Login with your superuser credentials

4. Click on **"Stocks"** in the sidebar

### Step 2: Import Stocks

1. Click the **"Import from CSV/Excel"** button (top right)

2. Choose your file:
   - CSV format (`.csv`)
   - Excel format (`.xlsx` or `.xls`)

3. Select the exchange:
   - **NSE** (National Stock Exchange) - adds `.NS` suffix
   - **BSE** (Bombay Stock Exchange) - adds `.BO` suffix

4. Click **"Import Stocks"**

5. Wait for processing (may take a few minutes for large files)

6. View the results:
   - ✅ **Green** - Successfully created new stocks
   - ℹ️ **Blue** - Updated existing stocks
   - ⚠️ **Yellow** - Failed imports with reasons

---

## File Format

### CSV Format (Recommended)

Create a CSV file with a `symbol` column:

```csv
symbol
RELIANCE
TCS
HDFCBANK
INFY
ICICIBANK
```

### Excel Format

Create an Excel file with column header `symbol` or `Symbol`:

| symbol    |
|-----------|
| RELIANCE  |
| TCS       |
| HDFCBANK  |
| INFY      |

**Note:** If no `symbol` column is found, the **first column** will be used.

---

## Example Files

### Sample CSV File

We've included `sample_stocks.csv` in the project root with 25 popular NSE stocks:

```
symbol
RELIANCE
TCS
HDFCBANK
INFY
ICICIBANK
SBIN
BHARTIARTL
... (and more)
```

### Download Real Stock Lists

You can download complete stock lists from:

**NSE:**
- https://www.nseindia.com/market-data/equity-market
- Click "Equity" → "Reports" → "Securities available for Trading"

**BSE:**
- https://www.bseindia.com/markets/equity/EQReports/ListofScripData.aspx

---

## What Gets Imported?

For each stock symbol, the system fetches:

| Field | Source | Description |
|-------|--------|-------------|
| **Symbol** | Your CSV | Stock symbol with exchange suffix |
| **Name** | Yahoo Finance | Company's full name |
| **Current Price** | Yahoo Finance | Latest market price |
| **Last Updated** | System | Timestamp of import |

---

## Features in Detail

### 1. **Automatic Suffix Addition**

If your CSV contains:
```
RELIANCE
TCS
```

And you select "NSE", it becomes:
```
RELIANCE.NS
TCS.NS
```

### 2. **Smart Column Detection**

The importer looks for columns in this order:
1. `symbol` (lowercase)
2. `Symbol` (capitalized)
3. `SYMBOL` (uppercase)
4. First column (fallback)

### 3. **Update Existing Stocks**

If a stock already exists:
- The **name** will be updated
- The **current price** will be updated
- The **last_updated** timestamp will be refreshed

### 4. **Error Handling**

Stocks that fail to import:
- Are skipped (won't break the import)
- Are listed in the warning message
- Common reasons:
  - Invalid symbol
  - Not tradable on selected exchange
  - Network issues
  - Yahoo Finance doesn't have data

---

## Tips & Best Practices

### ✅ Do:
- Use CSV format for best compatibility
- Verify symbol names before importing
- Import in batches of 50-100 for better performance
- Check failed imports and fix symbols

### ❌ Don't:
- Don't include duplicates in the same file
- Don't mix NSE and BSE stocks in one import (use two separate imports)
- Don't add `.NS` or `.BO` manually if using the exchange selector

---

## Troubleshooting

### Issue: "No stocks imported"

**Possible causes:**
1. CSV/Excel file has wrong column name
   - **Solution:** Name the column exactly `symbol`

2. Rows are empty
   - **Solution:** Remove empty rows from your file

3. Internet connection issues
   - **Solution:** Check your connection and retry

### Issue: "Many stocks failed to import"

**Possible causes:**
1. Invalid stock symbols
   - **Solution:** Verify symbols on NSE/BSE websites

2. Using wrong exchange
   - **Solution:** Make sure symbols are from the selected exchange

3. Rate limiting from Yahoo Finance
   - **Solution:** Wait a few minutes and retry

### Issue: "Template not found"

**Possible causes:**
1. Templates not in correct location
   - **Solution:** Ensure templates are in:
     - `stocks/templates/admin/csv_form.html`
     - `stocks/templates/admin/stocks/stock_changelist.html`

---

## Code

The import functionality is located in:
- **Admin logic:** `stocks/admin.py` - `StockAdmin.import_stocks_view()`
- **Templates:** `stocks/templates/admin/`
- **Dependencies:** `pandas`, `openpyxl`, `yfinance`

---

## Performance Notes

- **Small files (< 100 stocks):** ~1-2 minutes
- **Medium files (100-500 stocks):** ~5-10 minutes
- **Large files (500+ stocks):** ~15-30 minutes

The time depends on:
- Your internet speed
- Yahoo Finance API response time
- Server processing power

---

## Alternative: Management Command

If you prefer command-line, you can also create stocks using:

```bash
python manage.py populate_stocks
```

This uses the predefined stock list in `stocks/utils.py`.

---

## Summary

This bulk import feature makes it easy to add hundreds or thousands of stocks to your database in minutes, with automatic data fetching from Yahoo Finance! 🚀
