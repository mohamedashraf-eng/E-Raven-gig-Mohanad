document.addEventListener("DOMContentLoaded", function() {
    const signupForm = document.getElementById('signupForm');
    const password1 = document.querySelector('input[name="password1"]');
    const password2 = document.querySelector('input[name="password2"]');

    signupForm.addEventListener('submit', function(event) {
        if (password1.value !== password2.value) {
            event.preventDefault();
            alert("Passwords do not match.");
            password2.focus();
        }
    });
});
