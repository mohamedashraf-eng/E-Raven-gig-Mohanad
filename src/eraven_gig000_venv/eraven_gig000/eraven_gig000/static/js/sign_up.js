document.addEventListener("DOMContentLoaded", function () {
    const signUpForm = document.getElementById('sign-up-form');
    const loadingScreen = document.getElementById('loading-screen');
    const submitButton = signUpForm.querySelector('button[type="submit"]');

    signUpForm.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Clear previous errors and remove error styles
        document.querySelectorAll('.error').forEach(el => {
            el.textContent = '';
            el.classList.remove('error-show');
        });
        document.querySelectorAll('.form-control').forEach(input => {
            input.classList.remove('error-active');
        });

        // Collect form data
        const username = document.getElementById('id_username').value.trim();
        const email = document.getElementById('id_email').value.trim();
        const password1 = document.getElementById('id_password1').value;
        const password2 = document.getElementById('id_password2').value;

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
                // Display validation errors
                for (const [field, errors] of Object.entries(result)) {
                    const errorElement = document.getElementById(`error_${field}`);
                    const inputElement = document.getElementById(`id_${field}`);
                    if (errorElement && inputElement) {
                        errorElement.textContent = errors.join(' ');
                        errorElement.classList.add('error-show'); // Show the error message
                        inputElement.classList.add('error-active'); // Add red border to input
                    }
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
});
