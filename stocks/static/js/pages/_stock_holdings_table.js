function deleteStock(basketId, stockId, itemId, deleteUrl) {
    // Confirm deletion
    if (!confirm('Are you sure you want to remove this stock from the basket?')) {
        return;
    }

    // Show loading state
    const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
    if (row) {
        row.classList.add('loading');
    }

    // Use provided URL or fallback
    const url = deleteUrl || `/basket/${basketId}/stock/${stockId}/delete/`;
    // Send AJAX request to delete stock
    console.log(url);
    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        success: function (data) {
            if (data.success) {
                // Update the entire stock holdings table with new HTML
                if (data.stock_holdings_html) {
                    // Find the stock holdings container and replace it
                    const stockHoldingsContainer = document.querySelector('.stocks-table').parentElement;
                    stockHoldingsContainer.innerHTML = data.stock_holdings_html;
                }

                // Update investment amount in stats
                if (data.new_investment_amount !== undefined) {
                    const investmentElement = document.querySelector('.stats-grid .stat-card:first-child .stat-value');
                    if (investmentElement) {
                        investmentElement.textContent = '₹' + data.new_investment_amount.toFixed(2);
                    }
                }

                // Update portfolio stats
                if (data.total_current_value !== undefined) {
                    const currentValueElement = document.getElementById('total-current-value');
                    if (currentValueElement) {
                        currentValueElement.textContent = '₹' + data.total_current_value.toFixed(2);
                    }

                    const plElement = document.getElementById('total-profit-loss');
                    if (plElement) {
                        plElement.textContent = '₹' + data.total_profit_loss.toFixed(2);
                        plElement.className = 'stat-value ' + (data.total_profit_loss >= 0 ? 'positive' : 'negative');
                    }

                    const plPercentElement = document.getElementById('profit-loss-percentage');
                    if (plPercentElement) {
                        plPercentElement.textContent = data.profit_loss_percentage.toFixed(2) + '%';
                        plPercentElement.className = 'stat-value ' + (data.profit_loss_percentage >= 0 ? 'positive' : 'negative');
                    }
                }

                showMessage(data.message || 'Stock removed successfully!', 'success');
            } else {
                showMessage(data.error || 'Failed to remove stock', 'error');
                if (row) {
                    row.classList.remove('loading');
                }
            }
        },
        error: function (xhr, status, error) {
            console.error('Error:', error);
            showMessage('An error occurred while removing the stock', 'error');
            if (row) {
                row.classList.remove('loading');
            }
        }
    }); // Added missing semicolon here and ensured the function closes properly
}

// ========================================
// Add Stock Functionality with HTMX
// ========================================

function openAddStockModal() {
    const modal = document.getElementById('add-stock-modal');
    modal.style.display = 'flex';

    // Clear search input
    const searchInput = document.getElementById('stock-search-input');
    if (searchInput) {
        searchInput.value = '';
    }

    // Load stocks using HTMX ajax
    const stocksList = document.getElementById('available-stocks-list');
    if (stocksList) {
        // Show loading message
        stocksList.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--text-secondary);">Loading stocks...</div>';

        // Get the basket ID from the URL or data attribute
        const basketId = document.querySelector('[data-basket-id]')?.dataset.basketId;

        if (basketId) {
            // Use HTMX ajax to load stocks
            htmx.ajax('GET', `/basket/${basketId}/available-stocks/`, {
                target: '#available-stocks-list',
                swap: 'innerHTML'
            });
        }
    }
}

function closeAddStockModal() {
    const modal = document.getElementById('add-stock-modal');
    modal.style.display = 'none';
}

function filterAvailableStocks() {
    const searchTerm = document.getElementById('stock-search-input').value.toLowerCase();
    const stockItems = document.querySelectorAll('#available-stocks-list .stock-item');

    stockItems.forEach(item => {
        const symbol = item.getAttribute('data-symbol');
        const name = item.getAttribute('data-name');

        if (symbol.includes(searchTerm) || name.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// Close modal when clicking outside
document.addEventListener('click', function (event) {
    const modal = document.getElementById('add-stock-modal');
    if (event.target === modal) {
        closeAddStockModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeAddStockModal();
    }
});
