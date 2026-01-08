# Django Import-Export Integration Guide

## Overview

This project now uses **django-import-export** for handling data import and export in the Django admin interface. This provides a clean, professional interface for bulk data operations with support for multiple formats.

## Features

✅ **Multiple Format Support**: CSV, XLSX, JSON, and more
✅ **Automatic Yahoo Finance Integration**: Stock imports automatically fetch current prices and company names
✅ **Built-in Validation**: Pre-import validation with detailed error reports
✅ **Dry-run Mode**: Preview imports before committing to database
✅ **Export Functionality**: Export any model data in various formats
✅ **Skip Unchanged Records**: Only update records that have changed
✅ **Detailed Reports**: See exactly what was imported, updated, skipped, or failed

## Supported Models

All major models now have import/export functionality:

- **Stock** - Import/export stocks with automatic Yahoo Finance data fetching
- **Basket** - Import/export baskets with user relationships
- **BasketItem** - Import/export basket holdings
- **ChatGroup** - Import/export chat groups
- **ChatGroupMember** - Import/export group memberships
- **ChatMessage** - Import/export messages
- **TinyURL** - Import/export short URLs

## How to Import Data

### Method 1: Django Admin Interface (Recommended)

1. **Navigate to Django Admin**: Go to `/admin/`
2. **Select Model**: Choose the model you want to import (e.g., Stocks)
3. **Click Import Button**: Look for the "Import" button in the top-right corner
4. **Upload File**: 
   - Select your CSV, XLSX, or JSON file
   - Choose the file format from the dropdown
5. **Dry Run**: 
   - Review the import preview
   - Check for errors or warnings
   - See what will be created, updated, or skipped
6. **Confirm Import**: If everything looks good, click "Confirm import"

### Method 2: Command Line (Advanced)

You can also import data programmatically:

```python
from stocks.resources import StockResource
from import_export.formats import base_formats

# Load your file
dataset = open('stocks.csv', 'rb').read()

# Create resource instance
stock_resource = StockResource()

# Import with dry-run
result = stock_resource.import_data(
    dataset=dataset,
    dry_run=True,  # Set to False to actually save
    format=base_formats.CSV()
)

# Check results
print(f"Total rows: {result.totals['new'] + result.totals['update']}")
print(f"New: {result.totals['new']}")
print(f"Updated: {result.totals['update']}")
print(f"Errors: {result.totals['error']}")
```

## How to Export Data

1. **Navigate to Django Admin**: Go to `/admin/`
2. **Select Model**: Choose the model you want to export
3. **Click Export Button**: Look for the "Export" button in the top-right corner
4. **Choose Format**: Select CSV, XLSX, JSON, etc.
5. **Download**: The file will download immediately

You can also select specific records:
1. Use checkboxes to select specific records
2. Choose "Export selected..." from the Actions dropdown
3. Click "Go"

## Stock Import Format

### CSV Format Example

Create a CSV file with the following columns:

```csv
symbol,name,current_price
RELIANCE,Reliance Industries,
TCS,Tata Consultancy Services,
INFY,Infosys Limited,
```

**Important Notes:**
- **symbol**: Required. Can be with or without .NS/.BO suffix
- **name**: Optional. If not provided, automatically fetched from Yahoo Finance
- **current_price**: Optional. If not provided, automatically fetched from Yahoo Finance

### XLSX Format Example

Create an Excel file with columns: `symbol`, `name`, `current_price`

## Advanced Features

### Automatic Stock Data Fetching

When importing stocks, the system automatically:
1. Adds `.NS` suffix if not present (for NSE stocks)
2. Fetches company name from Yahoo Finance if not provided
3. Fetches current price from Yahoo Finance if not provided
4. Skips invalid or unavailable stocks

### Update Existing Records

The import system intelligently handles existing records:
- For **Stocks**: Uses `symbol` as unique identifier
- For **Baskets**: Uses `id` as unique identifier
- For **TinyURL**: Uses `short_code` as unique identifier

### Error Handling

If import fails:
1. **Validation Errors**: Shows which rows have issues
2. **Row Numbers**: Identifies exact rows with problems
3. **Error Messages**: Provides detailed error descriptions
4. **Rollback**: No changes are made if errors occur (in dry-run mode)

## Export Format Customization

Each model has predefined export column ordering for better readability. You can customize this in `stocks/resources.py`.

## Troubleshooting

### Issue: Import not showing errors
**Solution**: Make sure you're using the dry-run first to see validation errors

### Issue: Stocks not getting prices
**Solution**: 
- Check internet connection
- Verify stock symbol is valid on Yahoo Finance
- Try adding .NS or .BO suffix manually

### Issue: Foreign key relationships not working
**Solution**: 
- For User fields, use email address
- For Stock fields, use symbol
- For Basket fields, use basket name

## Best Practices

1. **Always use dry-run first**: Preview imports before committing
2. **Keep backups**: Export data before bulk imports
3. **Small batches**: Import in smaller batches for better error handling
4. **Validate data**: Clean your CSV/Excel files before importing
5. **Use templates**: Export existing data to use as import template

## File Format Support

| Format | Extension | Import | Export |
|--------|-----------|--------|--------|
| CSV    | .csv      | ✅     | ✅     |
| Excel  | .xlsx     | ✅     | ✅     |
| JSON   | .json     | ✅     | ✅     |
| YAML   | .yaml     | ✅     | ✅     |
| TSV    | .tsv      | ✅     | ✅     |
| ODS    | .ods      | ✅     | ✅     |

## Sample Import Files

Sample files are available in the project root:
- `sample.csv` - Example stock import file
- `sample_stocks.csv` - Larger stock dataset

## Configuration

Import/Export settings can be customized in `stocks/resources.py` and `stocks/admin.py`.

### Resource Options

```python
class Meta:
    skip_unchanged = True  # Skip records that haven't changed
    report_skipped = True  # Report skipped records
    import_id_fields = ['symbol']  # Fields to identify unique records
```

## Security Considerations

- Import/Export is only available to admin users
- All imports are logged
- Failed imports don't partially modify data
- Use dry-run to prevent accidental data corruption

## Performance Tips

- **Large files**: Import in batches of 1000-5000 records
- **Network calls**: Stock imports with Yahoo Finance are slower due to API calls
- **Memory**: Very large Excel files may require more memory

## Migration from Old Import System

The old custom CSV import system has been replaced with django-import-export. Benefits:
- ✅ Better UI/UX
- ✅ More formats supported
- ✅ Better error handling
- ✅ Dry-run capability
- ✅ Export functionality
- ✅ Less custom code to maintain

---

**Need Help?** Check the [django-import-export documentation](https://django-import-export.readthedocs.io/) for advanced usage.
