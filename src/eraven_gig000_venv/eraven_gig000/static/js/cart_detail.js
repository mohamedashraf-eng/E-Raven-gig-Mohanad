// static/js/cart_detail.js
document.addEventListener('DOMContentLoaded', function () {
    const removeButtons = document.querySelectorAll('.remove-btn');
    const removeToast = new bootstrap.Toast(document.getElementById('removeToast'));
  
    removeButtons.forEach(button => {
      button.addEventListener('click', function (e) {
        // Optional: Add confirmation prompt
        // if (!confirm('Are you sure you want to remove this item from your cart?')) {
        //   e.preventDefault();
        // }
  
        // Show toast notification
        removeToast.show();
      });
    });
  });
  