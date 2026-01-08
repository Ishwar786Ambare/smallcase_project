# 📊 Import/Export Feature - Django Import-Export

## Overview

This section explains the powerful import/export functionality available in the Django admin interface, powered by **django-import-export**.

## Features at a Glance

| Feature | Description |
|---------|-------------|
| **Import** | Bulk import stocks, baskets, and other data from CSV/Excel/JSON |
| **Export** | Export any data to multiple formats (CSV, XLSX, JSON, etc.) |
| **Auto-fetch** | Automatic stock price and name fetching from Yahoo Finance |
| **Dry-run** | Preview imports before committing to database |
| **Validation** | Automatic data validation with detailed error reports |
| **Formats** | CSV, XLSX, JSON, YAML, TSV, ODS |

## Quick Start

### Step 1: Access Admin Interface
```
http://localhost:8000/admin/
```

### Step 2: Navigate to Stocks
```
Admin → Stocks → Stock
```

### Step 3: Import Data

1. Click **"Import"** button (top-right corner)
2. Choose your file: `stock_import_template.csv`
3. Select format: **CSV**
4. Click **"Submit"**
5. Review the **dry-run preview**:
   - ✅ Rows to be created
   - ✅ Rows to be updated
   - ⚠️ Errors (if any)
6. Click **"Confirm import"**

### Step 4: Export Data

1. Click **"Export"** button (top-right corner)
2. Select format (CSV, XLSX, JSON, etc.)
3. File downloads automatically

## Import File Format

### Stock Import CSV

```csv
symbol,name,current_price
RELIANCE.NS,Reliance Industries,
TCS.NS,Tata Consultancy Services,
INFY.NS,Infosys,
```

**Important:**
- `symbol` is **required** (can be with or without .NS/.BO suffix)
- `name` is **optional** (auto-fetched from Yahoo Finance if blank)
- `current_price` is **optional** (auto-fetched from Yahoo Finance if blank)

### Basket Import CSV

```csv
id,user,name,description,investment_amount
1,user@example.com,Tech Stocks,Technology sector basket,100000
2,user@example.com,Pharma Stocks,Pharmaceutical stocks,50000
```

## Advanced Features

### 1. Automatic Data Fetching

When importing stocks, the system automatically:
- ✅ Adds `.NS` suffix if missing (NSE stocks)
- ✅ Fetches company name from Yahoo Finance
- ✅ Fetches current price from Yahoo Finance
- ✅ Validates stock symbols
- ✅ Skips invalid stocks with error messages

### 2. Update Existing Records

The import system intelligently handles duplicates:
- **Stocks**: Updates by `symbol` (unique identifier)
- **Baskets**: Updates by `id`
- **TinyURL**: Updates by `short_code`

### 3. Batch Operations

You can import hundreds or thousands of records at once:
- Recommended batch size: **1000-5000 records**
- Larger files: Split into multiple batches
- Progress tracking available in dry-run preview

### 4. Error Handling

Detailed error reports show:
- **Row number** where error occurred
- **Error type** (validation, missing field, etc.)
- **Error message** explaining the issue
- **Suggested fix** for common errors

Example error:
```
Row 5: Stock symbol 'INVALID' - Unable to fetch data from Yahoo Finance
```

## Export Options

### Export All Data
1. Go to model list page
2. Click **"Export"** button
3. All records exported in selected format

### Export Selected Records
1. Select records using checkboxes
2. Choose **"Export selected..."** from Actions dropdown
3. Click **"Go"**
4. Choose export format

### Export Formats

| Format | File Extension | Use Case |
|--------|---------------|----------|
| CSV | .csv | Excel, Google Sheets, data analysis |
| Excel | .xlsx | Advanced Excel features, formatting |
| JSON | .json | APIs, data interchange, backups |
| YAML | .yaml | Configuration, human-readable |
| TSV | .tsv | Tab-separated, legacy systems |

## Real-World Examples

### Example 1: Bulk Stock Import

**Scenario**: Import 50 Nifty 50 stocks

1. Create CSV file:
```csv
symbol,name,current_price
RELIANCE.NS,,
TCS.NS,,
INFY.NS,,
... (47 more stocks)
```

2. Import via admin
3. System auto-fetches all company names and prices
4. Review dry-run (shows all 50 stocks with fetched data)
5. Confirm import
6. All stocks ready to use!

### Example 2: Basket Migration

**Scenario**: Migrate baskets from another system

1. Export baskets from old system
2. Convert to CSV format:
```csv
user,name,description,investment_amount
user1@example.com,Growth Portfolio,High growth stocks,500000
user2@example.com,Value Portfolio,Undervalued stocks,300000
```

3. Import via admin
4. System creates baskets with user associations
5. Import basket items separately

### Example 3: Data Backup

**Scenario**: Regular data backups

1. Schedule weekly exports
2. Export all models to JSON
3. Store backups securely
4. Can restore anytime by importing

## Best Practices

### ✅ DO

- **Always use dry-run first** - Preview before committing
- **Keep backups** - Export before bulk imports
- **Small batches** - 1000-5000 records per import
- **Validate data** - Clean CSV/Excel before importing
- **Use templates** - Export existing data as import template

### ❌ DON'T

- Don't skip dry-run validation
- Don't import very large files (>10MB) without batching
- Don't import without backups
- Don't use spaces in column headers
- Don't mix different stock exchanges in same column

## Troubleshooting

### Problem: Import button not visible
**Solution**: 
- Ensure you're logged in as admin/staff user
- Check if `import_export` is in `INSTALLED_APPS`

### Problem: Stock prices not fetching
**Solution**:
- Check internet connection
- Verify stock symbol is correct (use .NS or .BO suffix)
- Yahoo Finance might be rate-limited (wait and retry)
- Some stocks may not be available on Yahoo Finance

### Problem: Import takes too long
**Solution**:
- Reduce batch size (split into smaller files)
- Stocks with Yahoo Finance fetching are slower
- Consider importing without dry-run if trusted data

### Problem: Foreign key errors
**Solution**:
- For User fields: Use email address
- For Stock fields: Use stock symbol
- For Basket fields: Use basket name
- Ensure referenced records exist before importing

## Performance Tips

### Fast Imports
- **Pre-fill data**: Provide name and price to avoid Yahoo Finance calls
- **Batch wisely**: 2000-3000 records optimal for speed
- **Off-peak**: Import during low-traffic times

### Memory Optimization
- **Large files**: Split into multiple smaller files
- **Excel files**: Use CSV format for better memory usage
- **Background tasks**: For very large imports, use management commands

## Sample Files Included

- ✅ `stock_import_template.csv` - Ready-to-use stock import template
- ✅ `sample.csv` - Sample stock data
- ✅ `sample_stocks.csv` - Larger stock dataset

## Integration with Other Features

### With Stock Price Updates
- Import stocks with current prices
- Use `python manage.py update_stock_prices` to refresh

### With Baskets
- Import stocks first
- Then import baskets
- Finally import basket items

### With User Management
- Ensure users exist before importing baskets
- Use email addresses for user references

## Security

- ✅ Admin-only access (staff/superuser required)
- ✅ All imports logged in Django admin logs
- ✅ CSRF protection enabled
- ✅ Dry-run prevents accidental data changes
- ✅ Validation before database commits

## API Usage (Advanced)

For programmatic access:

```python
from stocks.resources import StockResource

# Import
resource = StockResource()
dataset = resource.import_data(
    csv_data,
    dry_run=True,
    raise_errors=False
)

# Export
dataset = resource.export()
csv = dataset.csv
excel = dataset.xlsx
json = dataset.json
```

See `test_import_export.py` for complete examples.

## Documentation

- **Full Guide**: `DJANGO_IMPORT_EXPORT_GUIDE.md`
- **Summary**: `DJANGO_IMPORT_EXPORT_SUMMARY.md`
- **Official Docs**: https://django-import-export.readthedocs.io/

## Support

For issues or questions:
1. Check `DJANGO_IMPORT_EXPORT_GUIDE.md`
2. Review error messages carefully
3. Test with sample files first
4. Check Django admin logs

---

**Ready to import?** Start with `stock_import_template.csv` and follow the Quick Start guide above! 🚀
