// static/js/sign_up_step1.js

document.addEventListener('DOMContentLoaded', function () {
    const emailForm = document.getElementById('email-form');
    const emailInput = document.getElementById('id_email');

    emailForm.addEventListener('submit', function (e) {
        // Example: Client-side email format validation
        const emailValue = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(emailValue)) {
            e.preventDefault(); // Prevent form submission
            alert('Please enter a valid email address.');
            emailInput.focus();
        }

        // Optional: Add loading animations or disable the submit button to prevent multiple submissions
        const submitButton = emailForm.querySelector('.btn');
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
    });
});
