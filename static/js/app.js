// BankApp JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // PIN input formatting
    const pinInputs = document.querySelectorAll('input[type="password"][maxlength="4"]');
    pinInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            // Only allow numbers
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    });

    // Amount input formatting
    const amountInputs = document.querySelectorAll('input[type="number"]');
    amountInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            // Ensure positive values only
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[name*="phone"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            // Remove non-numeric characters except +
            this.value = this.value.replace(/[^+0-9]/g, '');
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Re-enable after 3 seconds to prevent permanent disable
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 3000);
            }
        });
    });

    // Store original button text
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(btn) {
        btn.setAttribute('data-original-text', btn.innerHTML);
    });

    // Balance refresh functionality
    const balanceElement = document.querySelector('.balance-amount');
    if (balanceElement) {
        setInterval(function() {
            // In a real app, you might want to fetch updated balance via AJAX
            // For now, we'll just add a subtle animation
            balanceElement.style.transform = 'scale(1.05)';
            setTimeout(function() {
                balanceElement.style.transform = 'scale(1)';
            }, 200);
        }, 30000); // Every 30 seconds
    }

    // Notification click handling
    const notifications = document.querySelectorAll('.notification-item');
    notifications.forEach(function(notification) {
        notification.addEventListener('click', function() {
            this.style.opacity = '0.7';
        });
    });

    // Copy to clipboard functionality for account numbers
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Show success message
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                btn.classList.add('btn-success');
                
                setTimeout(function() {
                    btn.innerHTML = originalText;
                    btn.classList.remove('btn-success');
                }, 2000);
            });
        });
    });

    // Real-time form validation
    const requiredInputs = document.querySelectorAll('input[required]');
    requiredInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (!this.value.trim()) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    });

    // Amount validation for transactions
    const transactionForms = document.querySelectorAll('form[action*="send"], form[action*="bill"]');
    transactionForms.forEach(function(form) {
        const amountInput = form.querySelector('input[name="amount"]');
        const balanceElement = document.querySelector('.balance-amount');
        
        if (amountInput && balanceElement) {
            amountInput.addEventListener('input', function() {
                const amount = parseFloat(this.value) || 0;
                const balance = parseFloat(balanceElement.textContent.replace('$', '')) || 0;
                
                if (amount > balance) {
                    this.classList.add('is-invalid');
                    this.setCustomValidity('Amount exceeds available balance');
                } else {
                    this.classList.remove('is-invalid');
                    this.setCustomValidity('');
                }
            });
        }
    });
});

// Utility functions
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'text-center';
    loadingDiv.innerHTML = '<div class="spinner"></div><p>Processing...</p>';
    loadingDiv.id = 'loading-overlay';
    document.body.appendChild(loadingDiv);
}

function hideLoading() {
    const loadingDiv = document.getElementById('loading-overlay');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function validatePhoneNumber(phone) {
    const phoneRegex = /^\+?[\d\s-()]+$/;
    return phoneRegex.test(phone) && phone.length >= 10;
}

function validateAmount(amount, maxAmount = null) {
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
        return false;
    }
    if (maxAmount && numAmount > maxAmount) {
        return false;
    }
    return true;
}