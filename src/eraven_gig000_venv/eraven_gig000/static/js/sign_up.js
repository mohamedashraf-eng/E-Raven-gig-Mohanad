// static/js/sign_up.js

document.addEventListener("DOMContentLoaded", function () {
    const signUpForm = document.getElementById('sign-up-form');
    const loadingScreen = document.getElementById('loading-screen');
    const submitButton = signUpForm.querySelector('button[type="submit"]');
    const usernameInput = document.getElementById('id_username'); // Added for username validation
    const emailInput = document.getElementById('id_email'); // Ensure this exists
    const password1Input = document.getElementById('id_password1');
    const password2Input = document.getElementById('id_password2');
    const strengthIndicatorBar = document.querySelector('.strength-bar');
    const strengthIndicatorText = document.querySelector('.strength-text');

    // Function to assess password strength
    function assessPasswordStrength(password) {
        let strength = 0;

        // Criteria
        const lengthCriteria = password.length >= 8;
        const uppercaseCriteria = /[A-Z]/.test(password);
        const lowercaseCriteria = /[a-z]/.test(password);
        const numberCriteria = /[0-9]/.test(password);
        const specialCharCriteria = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        // Increment strength based on criteria met
        if (lengthCriteria) strength++;
        if (uppercaseCriteria) strength++;
        if (lowercaseCriteria) strength++;
        if (numberCriteria) strength++;
        if (specialCharCriteria) strength++;

        return strength;
    }

    // Function to update strength indicator UI
    function updateStrengthIndicator(strength) {
        const strengthLevels = ['Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong'];
        const strengthColors = ['#ff4d4d', '#ff944d', '#ffd24d', '#b3ff66', '#66ff66'];

        if (strength === 0) {
            strengthIndicatorBar.style.width = '0%';
            strengthIndicatorText.textContent = '';
            return;
        }

        const percentage = (strength / 5) * 100;
        strengthIndicatorBar.style.width = `${percentage}%`;
        strengthIndicatorBar.style.backgroundColor = strengthColors[strength - 1];
        strengthIndicatorText.textContent = strengthLevels[strength - 1];
    }

    // Function to validate username
    function validateUsername(username) {
        const usernameErrors = [];

        // Check length
        if (username.length < 3) {
            usernameErrors.push("Username must be at least 3 characters long.");
        }
        if (username.length > 30) {
            usernameErrors.push("Username must not exceed 30 characters.");
        }

        // Check allowed characters
        const usernameRegex = /^[a-zA-Z0-9_]+$/;
        if (!usernameRegex.test(username)) {
            usernameErrors.push("Username can only contain letters, numbers, and underscores.");
        }

        return usernameErrors;
    }

    // Function to display error
    function displayError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        const inputElement = document.getElementById(elementId.replace('error_', 'id_'));
        if (errorElement && inputElement) {
            errorElement.textContent = message;
            errorElement.classList.add('error-show');
            inputElement.classList.add('error-active');
        }
    }

    // Function to clear all errors
    function clearErrors() {
        document.querySelectorAll('.error').forEach(el => {
            el.textContent = '';
            el.classList.remove('error-show');
        });
        document.querySelectorAll('.form-control').forEach(input => {
            input.classList.remove('error-active');
        });
    }

    // Event listener for password input to assess strength
    password1Input.addEventListener('input', function () {
        const password = password1Input.value;
        const strength = assessPasswordStrength(password);
        updateStrengthIndicator(strength);
    });

    signUpForm.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Clear previous errors and remove error styles
        clearErrors();

        // Collect form data
        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const password1 = password1Input.value;
        const password2 = password2Input.value;

        let hasError = false;

        // Client-side validation for username
        const usernameValidationErrors = validateUsername(username);
        if (usernameValidationErrors.length > 0) {
            displayError('error_username', usernameValidationErrors.join(' '));
            hasError = true;
        }

        // Client-side validation for email (basic check)
        if (!validateEmail(email)) {
            displayError('error_email', "Please enter a valid email address.");
            hasError = true;
        }

        // Client-side validation for password matching
        if (password1 !== password2) {
            displayError('error_password2', "Passwords do not match.");
            hasError = true;
        }

        // Client-side validation for password strength
        const strength = assessPasswordStrength(password1);
        if (strength < 3) { // Require at least 'Moderate' strength
            displayError('error_password1', "Password is too weak. Please choose a stronger password.");
            hasError = true;
        }

        if (hasError) {
            return; // Prevent form submission if there are errors
        }

        // Prepare data payload
        const data = {
            username: username,
            email: email,
            password1: password1,
            password2: password2
        };

        try {
            // Show loading screen and set button to processing state
            loadingScreen.style.display = 'block';
            submitButton.disabled = true;
            submitButton.textContent = "Processing..."; // Set button to "Processing..." during submission

            // Send POST request
            const response = await fetch(signUpForm.action, {
                method: 'POST', // Ensure method is POST
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Include CSRF token
                },
                body: JSON.stringify(data)
            });

            let result;
            try {
                result = await response.json();
            } catch (e) {
                result = {};
            }

            // Hide loading screen and reset button state
            loadingScreen.style.display = 'none';
            submitButton.disabled = false;
            submitButton.textContent = "Sign Up"; // Reset button text back to "Sign Up"

            if (response.ok) {
                // Redirect to 'check your email' page
                window.location.href = signUpForm.dataset.redirectUrl;
            } else {
                // Display validation errors from the server
                for (const [field, errors] of Object.entries(result)) {
                    displayError(`error_${field}`, errors.join(' '));
                }
            }
        } catch (error) {
            console.error('Error during sign-up:', error);
            // Hide loading screen and reset button state
            loadingScreen.style.display = 'none';
            submitButton.disabled = false;
            submitButton.textContent = "Sign Up"; // Reset button text back to "Sign Up"
            alert('An unexpected error occurred. Please try again later.');
        }
    });

    // Basic email validation function
    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});
