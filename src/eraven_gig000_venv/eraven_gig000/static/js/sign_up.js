// static/js/sign_up.js

document.addEventListener("DOMContentLoaded", function() {
    const passwordInput = document.getElementById('id_password1');
    const strengthIndicator = document.querySelector('.strength-indicator');

    passwordInput.addEventListener('input', function() {
        const strength = calculatePasswordStrength(passwordInput.value);
        strengthIndicator.textContent = `Strength: ${strength.label}`;
        strengthIndicator.style.color = strength.color;
    });

    function calculatePasswordStrength(password) {
        let score = 0;
        if (password.length >= 8) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/[a-z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[\W_]/.test(password)) score += 1;

        switch(score) {
            case 0:
            case 1:
            case 2:
                return { label: 'Weak', color: '#d9534f' }; // Red
            case 3:
            case 4:
                return { label: 'Moderate', color: '#f0ad4e' }; // Orange
            case 5:
                return { label: 'Strong', color: '#5cb85c' }; // Green
            default:
                return { label: 'Weak', color: '#d9534f' };
        }
    }
});
