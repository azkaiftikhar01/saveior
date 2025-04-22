// Currency conversion functionality
function setupCurrencyConversion() {
    const fromCurrency = document.getElementById('from_currency');
    const toCurrency = document.getElementById('to_currency');
    const amount = document.getElementById('amount');
    const convertBtn = document.getElementById('convert_btn');
    const result = document.getElementById('conversion_result');

    if (convertBtn && result) {
        convertBtn.addEventListener('click', async () => {
            const data = {
                from_currency: fromCurrency.value,
                to_currency: toCurrency.value,
                amount: amount.value
            };

            try {
                const response = await fetch('/convert-currency/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.success) {
                    document.getElementById('conversion_result').innerHTML = 
                        `${amount.value} ${fromCurrency.value} = ${result.converted_amount} ${toCurrency.value}`;
                } else {
                    document.getElementById('conversion_result').innerHTML = 
                        'Error: Failed to convert currency';
                }
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('conversion_result').innerHTML = 
                    'Error: Failed to convert currency';
            }
        });
    }
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupCurrencyConversion();
    initTooltips();
}); 