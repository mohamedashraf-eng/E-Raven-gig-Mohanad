// static/js/checkout.js

document.addEventListener('DOMContentLoaded', function () {
  const applyCouponBtn = document.getElementById('coupon-button');
  const couponCodeInput = document.getElementById('coupon_code');
  const feedbackDiv = document.getElementById('coupon-feedback');
  const totalCostSpan = document.getElementById('total-cost');

  applyCouponBtn.addEventListener('click', function () {
    const couponCode = couponCodeInput.value.trim();

    if (!couponCode) {
      displayFeedback('Please enter a coupon code.', 'danger');
      return;
    }

    // Disable button to prevent multiple clicks
    applyCouponBtn.disabled = true;
    applyCouponBtn.innerHTML = '<i class="bi bi-clock"></i> Applying...';

    // Send AJAX request to apply the coupon
    fetch(applyCouponUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'), // Function to get CSRF token
      },
      body: JSON.stringify({ 'coupon_code': couponCode }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        displayFeedback(data.message, 'success');
        // Display applied coupon
        displayAppliedCoupon(data.coupon_code, data.discount_amount);
        // Update total cost
        totalCostSpan.textContent = data.new_total;
        // Disable the coupon input and button
        couponCodeInput.disabled = true;
        applyCouponBtn.disabled = true;
        applyCouponBtn.innerHTML = '<i class="bi bi-tag"></i> Applied';
      } else {
        displayFeedback(data.message, 'danger');
        applyCouponBtn.disabled = false;
        applyCouponBtn.innerHTML = '<i class="bi bi-tag"></i> Apply';
      }
    })
    .catch(error => {
      console.error('Error:', error);
      displayFeedback('An error occurred while applying the coupon.', 'danger');
      applyCouponBtn.disabled = false;
      applyCouponBtn.innerHTML = '<i class="bi bi-tag"></i> Apply';
    });
  });

  // Function to display feedback messages
  function displayFeedback(message, type) {
    feedbackDiv.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;
  }

  // Function to display the applied coupon in the order summary
  function displayAppliedCoupon(couponCode, discountAmount) {
    const orderSummary = document.querySelector('.order-summary');
    // Remove existing applied-coupon if any
    const existingCoupon = document.querySelector('.applied-coupon');
    if (existingCoupon) {
      existingCoupon.remove();
    }

    const appliedCouponHTML = `
      <div class="applied-coupon alert alert-success d-flex justify-content-between align-items-center" role="alert">
        <div>
          <strong>Coupon Applied:</strong> "${couponCode}" - Discount: ${discountAmount}
        </div>
        <button type="button" class="btn-close" aria-label="Close" id="remove-coupon-btn"></button>
      </div>
    `;
    // Insert the applied coupon message above the total cost
    orderSummary.insertAdjacentHTML('beforeend', appliedCouponHTML);
  }

  // Function to get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Event delegation for dynamically added remove button
  document.body.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'remove-coupon-btn') {
      removeCoupon();
    }
  });

  function removeCoupon() {
    // Disable remove button to prevent multiple clicks
    const removeBtn = document.getElementById('remove-coupon-btn');
    if (removeBtn) {
      removeBtn.disabled = true;
      removeBtn.innerHTML = '<i class="bi bi-clock"></i>';
    }

    fetch(removeCouponUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({}),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          displayFeedback(data.message, 'success');
          // Remove the applied coupon alert
          const appliedCouponAlert = document.querySelector('.applied-coupon');
          if (appliedCouponAlert) {
            appliedCouponAlert.remove();
          }
          // Update total cost
          if (totalCostSpan) {
            totalCostSpan.textContent = data.new_total;
          }
          // Re-enable the coupon input and apply button
          if (couponCodeInput) couponCodeInput.disabled = false;
          if (applyCouponBtn) {
            applyCouponBtn.disabled = false;
            applyCouponBtn.innerHTML = '<i class="bi bi-tag"></i> Apply';
          }
        } else {
          displayFeedback(data.message, 'danger');
          if (removeBtn) {
            removeBtn.disabled = false;
            removeBtn.innerHTML = '<i class="bi bi-x"></i>';
          }
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        displayFeedback('An error occurred while removing the coupon.', 'danger');
        if (removeBtn) {
          removeBtn.disabled = false;
          removeBtn.innerHTML = '<i class="bi bi-x"></i>';
        }
      });
  }
});
