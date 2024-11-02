document.addEventListener('DOMContentLoaded', function () {
    const continueBtn = document.querySelector('.continue-btn');

    if (continueBtn && !continueBtn.disabled) {
        continueBtn.addEventListener('click', function (e) {
            // Add animations or additional client-side checks if desired
            e.target.classList.add('btn-click-animation');
        });
    } else {
        // If the button is disabled, notify the user to check their email
        continueBtn.addEventListener('click', function (e) {
            alert("Please activate your email before proceeding.");
        });
        
        // Optional: Add loading animations or disable the submit button to prevent multiple submissions
        const submitButton = emailForm.querySelector('.btn');
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
    }
});
