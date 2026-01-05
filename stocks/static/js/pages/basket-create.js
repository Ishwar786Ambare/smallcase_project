/* ========================================
   BASKET-CREATE - JavaScript
   Extracted from basket_create.j2
   ======================================== */


function updateCount() {
    console.log('Updating count');
    const checked = document.querySelectorAll('input[name="stocks"]:checked').length;
    document.getElementById('count').textContent = checked;

    // Visual feedback for minimum requirement
    const countDisplay = document.getElementById('selectedCount');
    if (checked < 2) {
        countDisplay.style.background = '#ef4444'; // Keep red for error/warning
    } else {
        countDisplay.style.background = 'var(--primary-color)';
    }
}

// Form validation before submit
document.querySelector('form').addEventListener('submit', function (e) {
    const checked = document.querySelectorAll('input[name="stocks"]:checked').length;
    if (checked < 2) {
        e.preventDefault();
        alert('Please select at least 2 stocks for your basket.');
        return false;
    }
});

function filterStocks() {
    const searchTerm = document.getElementById('searchStock').value.toLowerCase();
    const stockItems = document.querySelectorAll('.stock-checkbox');

    stockItems.forEach(item => {
        const name = item.getAttribute('data-name').toLowerCase();
        const symbol = item.getAttribute('data-symbol').toLowerCase();

        if (name.includes(searchTerm) || symbol.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// Initialize count on page load
updateCount();
