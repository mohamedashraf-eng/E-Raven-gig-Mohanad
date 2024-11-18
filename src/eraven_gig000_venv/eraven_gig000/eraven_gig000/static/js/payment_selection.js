// static/js/payment_selection.js

document.addEventListener('DOMContentLoaded', function () {
  const paymentCards = document.querySelectorAll('.payment-card');
  const gatewayInput = document.getElementById('gateway-input');
  const paymentForm = document.querySelector('.payment-form');
  const invalidFeedback = document.getElementById('gateway-invalid-feedback');

  paymentCards.forEach(card => {
    card.addEventListener('click', function () {
      // Remove 'selected' class from all cards
      paymentCards.forEach(c => c.classList.remove('selected'));
      
      // Add 'selected' class to the clicked card
      this.classList.add('selected');
      
      // Set the hidden input value
      gatewayInput.value = this.getAttribute('data-gateway');
      
      // Hide invalid feedback if visible
      if (invalidFeedback.style.display === 'block') {
        invalidFeedback.style.display = 'none';
      }
    });
  });

  paymentForm.addEventListener('submit', function (event) {
    if (!gatewayInput.value) {
      event.preventDefault();
      invalidFeedback.style.display = 'block';
    }
  });
});
