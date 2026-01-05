# Tiny URL Feature for Basket Sharing

## Overview
The Tiny URL feature allows users to generate shortened URLs for sharing their stock baskets with others. This makes it easier to share basket information via social media, messaging apps, or any platform where shorter URLs are preferred.

## Features

### 1. **Short URL Generation**
- Each basket can have a tiny URL created for it
- URLs are automatically generated with a unique 6-character code
- Example: `http://localhost:1234/s/ytQv29`

### 2. **One-Click Sharing**
- Click the "🔗 Share Basket" button on any basket detail page
- A modal will appear with the shortened URL
- Click "Copy" to copy the URL to your clipboard

### 3. **Click Tracking**
- Each tiny URL tracks how many times it has been accessed
- Statistics are displayed in the share modal
- Example: "This link has been clicked 1 time"

### 4. **Persistent Links**
- Once created, a tiny URL is reused for the same basket
- The same short code will be returned on subsequent share requests
- Links remain active unless explicitly deactivated

### 5. **Automatic Redirect**
- Visiting a tiny URL automatically redirects to the basket detail page
- Works for both logged-in and logged-out users
- The basket owner's data is displayed

## Technical Implementation

### Models
- **TinyURL Model** (`stocks/models.py`)
  - `short_code`: Unique 6-character code
  - `original_url`: Full basket URL
  - `basket`: Foreign key to the Basket model
  - `created_by`: User who created the link
  - `click_count`: Number of times the link was accessed
  - `is_active`: Boolean to enable/disable links
  - `expires_at`: Optional expiration date

### Views
- **create_tiny_url** (`/basket/<id>/share/`)
  - Generates or retrieves existing tiny URL for a basket
  - Returns JSON with short URL and statistics
  
- **redirect_tiny_url** (`/s/<short_code>/`)
  - Redirects to the original basket detail page
  - Increments click counter
  - Shows error if link is expired or inactive

- **tiny_url_stats** (`/s/<short_code>/stats/`)
  - Returns statistics for a specific tiny URL
  - Only accessible by the link creator

### Frontend
- Share button added to basket detail page
- Modal dialog for displaying and copying the URL
- JavaScript functions for:
  - Creating tiny URLs via AJAX
  - Copying to clipboard with visual feedback
  - Displaying click statistics

## Usage

### For Users
1. Navigate to any basket's detail page
2. Click the "🔗 Share Basket" button
3. A modal will appear showing your short URL
4. Click "Copy" to copy the link
5. Share the link with anyone!

### For Administrators
- View all tiny URLs in the Django admin panel
- Filter by active status, creation date, etc.
- See click statistics for each link
- Deactivate or delete links as needed
- Access path: `/admin/stocks/tinyurl/`

## Security Considerations

1. **Access Control**: Anyone with the link can view the basket (read-only)
2. **No Editing**: Shared links only allow viewing, not editing basket data
3. **Link Deactivation**: Links can be deactivated by admins if needed
4. **Expiration**: Optional expiration dates can be set for temporary sharing

## URL Structure

- **Create/Get Tiny URL**: `GET /basket/<basket_id>/share/`
- **Redirect**: `GET /s/<short_code>/`
- **Statistics**: `GET /s/<short_code>/stats/`

## Database Schema

```sql
CREATE TABLE stocks_tinyurl (
    id INTEGER PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    original_url VARCHAR(500) NOT NULL,
    basket_id INTEGER,
    created_by_id INTEGER,
    created_at DATETIME NOT NULL,
    expires_at DATETIME,
    click_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (basket_id) REFERENCES stocks_basket(id),
    FOREIGN KEY (created_by_id) REFERENCES user_customuser(id)
);
```

## Future Enhancements

Potential improvements for the feature:
1. QR code generation for tiny URLs
2. Social media sharing buttons (Twitter, WhatsApp, etc.)
3. Analytics dashboard for tracking link performance
4. Custom short codes (vanity URLs)
5. Expiration date configuration in UI
6. Batch URL generation for multiple baskets
7. PDF export with QR code and tiny URL

## Examples

### Creating a Short URL (API Response)
```json
{
    "success": true,
    "short_code": "ytQv29",
    "short_url": "http://127.0.0.1:1234/s/ytQv29",
    "original_url": "http://127.0.0.1:1234/en/basket/9/",
    "click_count": 0
}
```

### Accessing Statistics
```json
{
    "success": true,
    "short_code": "ytQv29",
    "original_url": "http://127.0.0.1:1234/en/basket/9/",
    "click_count": 5,
    "created_at": "2026-01-05 10:45:32",
    "expires_at": null,
    "is_active": true,
    "is_expired": false
}
```

## Testing

The feature has been tested with:
- Creating new tiny URLs ✓
- Reusing existing URLs ✓
- Click tracking ✓
- Clipboard copy functionality ✓
- URL redirection ✓
- Modal display and animations ✓

All functionality is working as expected!
