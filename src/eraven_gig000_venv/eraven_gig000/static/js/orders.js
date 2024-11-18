// static/js/orders.js

document.addEventListener('DOMContentLoaded', () => {
    const incrementButtons = document.querySelectorAll('.increment');
    const decrementButtons = document.querySelectorAll('.decrement');
    const quantityInputs = document.querySelectorAll('.quantity-input');

    incrementButtons.forEach(button => {
        button.addEventListener('click', () => {
            const input = button.parentElement.querySelector('.quantity-input');
            let value = parseInt(input.value);
            if (!isNaN(value)) {
                input.value = value + 1;
                updateCart(itemId=input.closest('tr').dataset.productId, quantity=value + 1);
            }
        });
    });

    decrementButtons.forEach(button => {
        button.addEventListener('click', () => {
            const input = button.parentElement.querySelector('.quantity-input');
            let value = parseInt(input.value);
            if (!isNaN(value) && value > 1) {
                input.value = value - 1;
                updateCart(itemId=input.closest('tr').dataset.productId, quantity=value - 1);
            }
        });
    });

    quantityInputs.forEach(input => {
        input.addEventListener('change', () => {
            let value = parseInt(input.value);
            if (isNaN(value) || value < 1) {
                input.value = 1;
                value = 1;
            }
            updateCart(itemId=input.closest('tr').dataset.productId, quantity=value);
        });
    });
});

function updateCart(itemId, quantity) {
    // Implement AJAX request to update the cart
    // This is a placeholder function and needs to be implemented based on your backend
    console.log(`Update cart: Item ID = ${itemId}, Quantity = ${quantity}`);
    // Example using fetch:
    /*
    fetch(`/api/v1/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // Function to get CSRF token
        },
        body: JSON.stringify({ quantity: quantity }),
    })
    .then(response => response.json())
    .then(data => {
        // Update the DOM based on the response
        // e.g., update cost and total
    })
    .catch(error => console.error('Error updating cart:', error));
    */
}
